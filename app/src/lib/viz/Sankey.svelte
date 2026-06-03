<script lang="ts">
	import { onMount } from 'svelte';
	import { sankey as d3Sankey, sankeyLinkHorizontal, sankeyLeft } from 'd3-sankey';
	import * as d3 from 'd3';
	import { filters, type ColorMetric } from '$lib/stores/filters';
	import {
		selection,
		togglePin,
		isSameEdge,
		isco1ToNodeId,
		type EdgeKey,
		type SearchTarget
	} from '$lib/stores/selection';
	import { datasets, startDatasets } from '$lib/stores/data';
	import { computeActiveEdges, computeEdgeChain, edgeKey } from '$lib/utils/path';
	import { easter } from '$lib/stores/easter';

	type DrillChild = {
		id: string;
		label: string;
		share: number;
		salaryMul?: number;
		employMul?: number;
		adeqMul?: number;
		source?: string;
	};

	type RawNode = {
		id: string;
		layer: number;
		label: string;
		category: 'origin' | 'study' | 'occupation' | 'outcome';
		branca?: string;
		isco?: string;
		outcome_score?: number;
		children?: DrillChild[];
	};

	type RawEdgeMeta = {
		sourceDataset: string;
		placeholder?: boolean;
		pctOfSource?: number;
		medianSalary?: number;
		salaryF?: number;
		salaryM?: number;
		pctEmployed?: number;
		pctAdequate?: number;
		medianMonthsToJob?: number;
		composite?: number;
		genderRatio?: { F: number; M: number };
		wave?: number;
	};

	type RawEdge = {
		source: string;
		target: string;
		value: number;
		meta: RawEdgeMeta;
	};

	type Payload = {
		version: string;
		generated_at: string;
		title: string;
		scope: string;
		nodes: RawNode[];
		edges: RawEdge[];
		seed_totals: Record<string, number>;
		stats?: { node_count: number; edge_count: number; placeholder_edges: number };
	};

	let svgEl = $state<SVGSVGElement | null>(null);
	let containerEl = $state<HTMLDivElement | null>(null);
	let tooltip = $state<{ x: number; y: number; html: string } | null>(null);
	let status = $state<'loading' | 'ready' | 'fetch-error' | 'render-error'>('loading');
	let errorMessage = $state<string>('');
	let payload = $state<Payload | null>(null);
	let lastDims = { w: 0, h: 0 };
	let easterUnlocked = $state(false);
	let expandedNodes = $state<Set<string>>(new Set());

	const CATEGORY_COLOR: Record<RawNode['category'], string> = {
		origin: '#7B8395',
		study: '#4FB6D0',
		occupation: '#FFC857',
		outcome: '#E0533D'
	};

	const EASTER_NODES: RawNode[] = [
		{ id: 'easter__refusal', label: 'Negar la pregunta', layer: 3, category: 'study' },
		{ id: 'easter__revolt', label: 'Revolucionar-se', layer: 6, category: 'occupation' },
		{ id: 'easter__utopia', label: 'Salari 0 € · Felicitat 100', layer: 7, category: 'outcome', outcome_score: 1.0 }
	];

	const EASTER_EDGES: RawEdge[] = [
		{
			source: 'start__eso',
			target: 'easter__refusal',
			value: 1200,
			meta: {
				sourceDataset: 'easter-egg',
				placeholder: true,
				composite: 0.9,
				pctEmployed: 0
			}
		},
		{
			source: 'easter__refusal',
			target: 'easter__revolt',
			value: 1200,
			meta: { sourceDataset: 'easter-egg', placeholder: true, composite: 0.95 }
		},
		{
			source: 'easter__revolt',
			target: 'easter__utopia',
			value: 1200,
			meta: {
				sourceDataset: 'easter-egg',
				placeholder: true,
				composite: 1.0,
				medianSalary: 0,
				pctAdequate: 1.0
			}
		}
	];

	const integerFormat = d3.format(',');
	const pctFormat = d3.format('.0%');
	const salaryFormat = (n: number) => integerFormat(Math.round(n)) + ' €';

	// Color scales per metric
	const SCALES: Record<ColorMetric, d3.ScaleLinear<string, string>> = {
		composite: d3
			.scaleLinear<string>()
			.domain([0.0, 0.35, 0.6, 0.85])
			.range(['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D'])
			.clamp(true),
		salary: d3
			.scaleLinear<string>()
			.domain([16000, 22000, 28000, 35000])
			.range(['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D'])
			.clamp(true),
		employed: d3
			.scaleLinear<string>()
			.domain([0.6, 0.78, 0.88, 0.96])
			.range(['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D'])
			.clamp(true),
		adequate: d3
			.scaleLinear<string>()
			.domain([0.35, 0.55, 0.75, 0.92])
			.range(['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D'])
			.clamp(true)
	};

	function metricValue(meta: RawEdgeMeta, metric: ColorMetric): number | undefined {
		switch (metric) {
			case 'composite':
				return meta.composite;
			case 'salary':
				return meta.medianSalary;
			case 'employed':
				return meta.pctEmployed;
			case 'adequate':
				return meta.pctAdequate;
		}
	}

	function colorEdge(meta: RawEdgeMeta, target: RawNode | undefined, metric: ColorMetric): string {
		const v = metricValue(meta, metric);
		if (typeof v === 'number') return SCALES[metric](v);
		// Fallback: outcome edges have no AQU-style meta, colour by outcome_score
		if (target?.outcome_score !== undefined) return SCALES.composite(target.outcome_score);
		if (target?.category && CATEGORY_COLOR[target.category]) return CATEGORY_COLOR[target.category];
		return '#7B8395';
	}

	function genderAdjustedSalary(meta: RawEdgeMeta, gender: 'all' | 'F' | 'M'): number | undefined {
		if (gender === 'all') return meta.medianSalary;
		if (meta.genderRatio) {
			// Heuristic: if we don't have F/M split, project from modal using bretxa proxy.
			// AQU public data typically shows ~10% gap; apply as ±5% around modal.
			if (meta.medianSalary !== undefined) {
				const gap = 0.05;
				return gender === 'F' ? meta.medianSalary * (1 - gap) : meta.medianSalary * (1 + gap);
			}
		}
		return meta.medianSalary;
	}

	// ── Render ─────────────────────────────────────────────────────────
	function render(p: Payload, width: number, height: number) {
		if (!svgEl) return;
		lastDims = { w: width, h: height };
		const svg = d3.select(svgEl);
		svg.selectAll('*').remove();

		const extraNodes = easterUnlocked ? EASTER_NODES : [];
		const extraEdges = easterUnlocked ? EASTER_EDGES : [];

		// Apply drill-down expansion: replace each expanded node with its children
		// and rewrite the edges that touched it. Children share the parent's layer.
		const expandedSet = expandedNodes;
		const baseNodes = [...p.nodes, ...extraNodes];
		const baseEdges = [...p.edges, ...extraEdges];

		const replacedNodes = new Map<string, DrillChild[]>();
		for (const n of baseNodes) {
			if (n.children && n.children.length > 0 && expandedSet.has(n.id)) {
				replacedNodes.set(n.id, n.children);
			}
		}

		const finalNodes: RawNode[] = [];
		for (const n of baseNodes) {
			if (replacedNodes.has(n.id)) {
				for (const c of replacedNodes.get(n.id)!) {
					finalNodes.push({
						id: c.id,
						layer: n.layer,
						label: c.label,
						category: n.category,
						branca: n.branca,
						isco: n.isco
					});
				}
			} else {
				finalNodes.push(n);
			}
		}

		const childSrc = (id: string) => {
			for (const [parent, kids] of replacedNodes) {
				const c = kids.find((k) => k.id === id);
				if (c) return { parent, child: c };
			}
			return null;
		};

		const finalEdges: RawEdge[] = [];
		for (const e of baseEdges) {
			const sExp = replacedNodes.get(e.source);
			const tExp = replacedNodes.get(e.target);

			if (!sExp && !tExp) {
				finalEdges.push(e);
				continue;
			}

			// Replace endpoints with each child, scaled by share.
			const sources = sExp ? sExp.map((c) => ({ id: c.id, share: c.share, child: c })) : [{ id: e.source, share: 1, child: null as DrillChild | null }];
			const targets = tExp ? tExp.map((c) => ({ id: c.id, share: c.share, child: c })) : [{ id: e.target, share: 1, child: null as DrillChild | null }];

			for (const s of sources) {
				for (const t of targets) {
					const share = s.share * t.share;
					const meta = { ...e.meta };
					// Apply child modifiers if the child is the "downstream" anchor:
					// scale composite-driving metrics (salary, employ, adequacy) so the
					// expanded children carry visibly different mètric contrasts.
					const mod = (t.child ?? s.child) as DrillChild | null;
					if (mod) {
						if (meta.medianSalary !== undefined && mod.salaryMul !== undefined) {
							meta.medianSalary = Math.round(meta.medianSalary * mod.salaryMul);
						}
						if (meta.pctEmployed !== undefined && mod.employMul !== undefined) {
							meta.pctEmployed = Math.max(0, Math.min(1, meta.pctEmployed * mod.employMul));
						}
						if (meta.pctAdequate !== undefined && mod.adeqMul !== undefined) {
							meta.pctAdequate = Math.max(0, Math.min(1, meta.pctAdequate * mod.adeqMul));
						}
						if (meta.composite !== undefined && (mod.salaryMul || mod.employMul || mod.adeqMul)) {
							const avg = ((mod.salaryMul ?? 1) + (mod.employMul ?? 1) + (mod.adeqMul ?? 1)) / 3;
							meta.composite = Math.max(0, Math.min(1, meta.composite * avg));
						}
						if (mod.source) meta.sourceDataset = mod.source;
					}
					finalEdges.push({ source: s.id, target: t.id, value: Math.round(e.value * share), meta });
				}
			}
		}

		const ids = new Set(finalNodes.map((n) => n.id));
		const safeNodes = finalNodes.map((n) => ({ ...n }));
		const safeLinks = finalEdges
			.filter((e) => ids.has(e.source) && ids.has(e.target) && e.value > 0)
			.map((e) => ({ source: e.source, target: e.target, value: e.value, meta: e.meta }));

		const margin = { top: 20, right: 240, bottom: 20, left: 20 };
		const innerW = Math.max(640, width - margin.left - margin.right);
		const innerH = Math.max(420, height - margin.top - margin.bottom);

		const layout = d3Sankey<
			{ id: string; label: string; category: string; layer: number },
			{ value: number; meta: RawEdgeMeta }
		>()
			.nodeId((d) => (d as unknown as { id: string }).id)
			.nodeAlign(sankeyLeft)
			.nodeWidth(14)
			.nodePadding(14)
			.extent([
				[1, 1],
				[innerW, innerH]
			]);

		let result;
		try {
			result = layout({ nodes: safeNodes as never, links: safeLinks as never });
		} catch (err) {
			console.error('d3-sankey layout failed:', err);
			throw err;
		}

		svg
			.attr('viewBox', `0 0 ${innerW + margin.left + margin.right} ${innerH + margin.top + margin.bottom}`)
			.attr('preserveAspectRatio', 'xMidYMid meet');

		const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

		// ── Links ──────────────────────────────────────────────────────
		const link = g
			.append('g')
			.attr('fill', 'none')
			.attr('class', 'links')
			.attr('role', 'list')
			.selectAll('path')
			.data(result.links)
			.enter()
			.append('path')
			.attr('d', sankeyLinkHorizontal())
			.attr('stroke-width', (d) => Math.max(1, (d as unknown as { width: number }).width))
			.attr('cursor', 'pointer')
			.attr('tabindex', 0)
			.attr('role', 'listitem')
			.attr('aria-label', (d) => {
				const dd = d as unknown as {
					source: RawNode;
					target: RawNode;
					value: number;
					meta: RawEdgeMeta;
				};
				const parts = [`${dd.source.label} cap a ${dd.target.label}`, `volum ${integerFormat(dd.value)}`];
				if (dd.meta.pctEmployed !== undefined) parts.push(`ocupació ${pctFormat(dd.meta.pctEmployed)}`);
				if (dd.meta.medianSalary !== undefined)
					parts.push(`salari modal ${integerFormat(Math.round(dd.meta.medianSalary))} euros`);
				return parts.join(', ');
			});

		link
			.on('mousemove', (event, d) => {
				const dd = d as unknown as {
					source: RawNode;
					target: RawNode;
					value: number;
					meta: RawEdgeMeta;
				};
				const f = currentFilters;
				const salary = genderAdjustedSalary(dd.meta, f.gender);
				const bits: string[] = [];
				bits.push(`<strong>${dd.source.label}</strong> → <strong>${dd.target.label}</strong>`);
				bits.push(`Volum: <span class="num">${integerFormat(dd.value)}</span>`);
				if (dd.meta.pctOfSource !== undefined) bits.push(`% origen: ${pctFormat(dd.meta.pctOfSource)}`);
				if (dd.meta.pctEmployed !== undefined) bits.push(`Ocupats: ${pctFormat(dd.meta.pctEmployed)}`);
				if (dd.meta.pctAdequate !== undefined) bits.push(`Adequació al títol: ${pctFormat(dd.meta.pctAdequate)}`);
				if (salary !== undefined) {
					const tag = f.gender === 'all' ? 'modal' : f.gender === 'F' ? 'mitjana (dones)' : 'mitjana (homes)';
					bits.push(`Salari ${tag}: ${salaryFormat(salary)}`);
				}
				if (dd.meta.medianMonthsToJob !== undefined)
					bits.push(`Mesos fins primera feina: ${dd.meta.medianMonthsToJob}`);
				if (dd.meta.genderRatio)
					bits.push(`Composició gènere: F ${pctFormat(dd.meta.genderRatio.F)} · M ${pctFormat(dd.meta.genderRatio.M)}`);
				if (dd.meta.composite !== undefined)
					bits.push(`Empleabilitat composta: <span class="num">${dd.meta.composite.toFixed(2)}</span>`);
				const waveBit = dd.meta.wave ? ` · onada ${dd.meta.wave}` : '';
				const provenance = dd.meta.placeholder ? ' (estimació)' : '';
				if (dd.meta.sourceDataset)
					bits.push(`<em class="src">font: ${dd.meta.sourceDataset}${waveBit}${provenance}</em>`);
				const rect = containerEl?.getBoundingClientRect();
				tooltip = {
					x: event.clientX - (rect?.left ?? 0) + 14,
					y: event.clientY - (rect?.top ?? 0) + 14,
					html: bits.join('<br/>')
				};
			})
			.on('mouseleave', () => {
				tooltip = null;
			})
			.on('click', (_event, d) => {
				const dd = d as unknown as { source: RawNode; target: RawNode };
				togglePin({ source: dd.source.id, target: dd.target.id });
			})
			.on('keydown', (event, d) => {
				const ke = event as KeyboardEvent;
				const dd = d as unknown as { source: RawNode; target: RawNode };
				if (ke.key === 'Enter' || ke.key === ' ') {
					ke.preventDefault();
					togglePin({ source: dd.source.id, target: dd.target.id });
				} else if (ke.key === 'Escape') {
					togglePin({ source: dd.source.id, target: dd.target.id }); // unpin if pinned
				}
			})
			.on('focus', (event, d) => {
				const dd = d as unknown as {
					source: RawNode;
					target: RawNode;
					value: number;
					meta: RawEdgeMeta;
				};
				const pathEl = event.currentTarget as SVGPathElement;
				const bbox = pathEl.getBoundingClientRect();
				const rect = containerEl?.getBoundingClientRect();
				const f = currentFilters;
				const salary = genderAdjustedSalary(dd.meta, f.gender);
				const bits: string[] = [];
				bits.push(`<strong>${dd.source.label}</strong> → <strong>${dd.target.label}</strong>`);
				bits.push(`Volum: <span class="num">${integerFormat(dd.value)}</span>`);
				if (dd.meta.pctEmployed !== undefined) bits.push(`Ocupats: ${pctFormat(dd.meta.pctEmployed)}`);
				if (dd.meta.pctAdequate !== undefined) bits.push(`Adequació al títol: ${pctFormat(dd.meta.pctAdequate)}`);
				if (salary !== undefined) bits.push(`Salari: ${salaryFormat(salary)}`);
				tooltip = {
					x: bbox.right - (rect?.left ?? 0) + 14,
					y: bbox.top - (rect?.top ?? 0),
					html: bits.join('<br/>')
				};
			})
			.on('blur', () => {
				tooltip = null;
			});

		// Build a map id→original-node so we know which rendered nodes have
		// children available (parents that haven't been expanded yet).
		const originalById = new Map<string, RawNode>();
		for (const n of p.nodes) originalById.set(n.id, n);

		const isExpandable = (n: RawNode) =>
			(n.children && n.children.length > 0) ?? false;
		const isExpanded = (n: RawNode) => expandedSet.has(n.id);
		const isChild = (n: RawNode) => n.id.startsWith('titul__');

		// ── Nodes ──────────────────────────────────────────────────────
		const node = g
			.append('g')
			.attr('class', 'nodes')
			.selectAll('g')
			.data(result.nodes)
			.enter()
			.append('g')
			.attr('class', (d) => {
				const nd = d as unknown as RawNode;
				const cls = ['node'];
				if (isExpandable(nd)) cls.push('expandable');
				if (isChild(nd)) cls.push('child');
				return cls.join(' ');
			})
			.attr('cursor', (d) => (isExpandable(d as unknown as RawNode) || isChild(d as unknown as RawNode) ? 'pointer' : 'default'))
			.on('click', (_event, d) => {
				const nd = d as unknown as RawNode;
				if (isExpandable(nd)) {
					expandedNodes = new Set([...expandedNodes, nd.id]);
					measureAndRender();
				} else if (isChild(nd)) {
					// Collapse the parent that owns this child
					for (const [pid, kids] of replacedNodes) {
						if (kids.some((k) => k.id === nd.id)) {
							const next = new Set(expandedNodes);
							next.delete(pid);
							expandedNodes = next;
							measureAndRender();
							break;
						}
					}
				}
			});

		node
			.append('rect')
			.attr('x', (d) => (d as unknown as { x0: number }).x0)
			.attr('y', (d) => (d as unknown as { y0: number }).y0)
			.attr('height', (d) => {
				const nd = d as unknown as { y0: number; y1: number };
				return Math.max(1, nd.y1 - nd.y0);
			})
			.attr('width', (d) => {
				const nd = d as unknown as { x0: number; x1: number };
				return nd.x1 - nd.x0;
			})
			.attr('fill', (d) => CATEGORY_COLOR[(d as unknown as RawNode).category] ?? '#7B8395')
			.attr('opacity', 0.92);

		node
			.append('text')
			.attr('x', (d) => {
				const nd = d as unknown as { x0: number; x1: number };
				return nd.x1 < innerW / 2 ? nd.x1 + 8 : nd.x0 - 8;
			})
			.attr('y', (d) => {
				const nd = d as unknown as { y0: number; y1: number };
				return (nd.y0 + nd.y1) / 2;
			})
			.attr('dy', '0.32em')
			.attr('text-anchor', (d) => {
				const nd = d as unknown as { x0: number; x1: number };
				return nd.x1 < innerW / 2 ? 'start' : 'end';
			})
			.attr('fill', 'var(--ink-primary)')
			.attr('font-size', (d) => (isChild(d as unknown as RawNode) ? 11 : 12))
			.attr('font-family', 'var(--font-sans)')
			.text((d) => {
				const nd = d as unknown as RawNode;
				const isExp = isExpandable(nd);
				const prefix = isExp ? '+ ' : isChild(nd) ? '↳ ' : '';
				return prefix + nd.label;
			});

		applyVisualState();
	}

	// ── Reactive visual state (no re-layout, only attrs) ───────────────
	let currentFilters = $state<{ gender: 'all' | 'F' | 'M'; branca: string[]; colorMetric: ColorMetric }>({
		gender: 'all',
		branca: [],
		colorMetric: 'composite'
	});
	let currentPinned: EdgeKey | null = $state(null);
	let currentSearchTarget: SearchTarget | null = $state(null);

	function intersect(a: Set<string> | null, b: Set<string> | null): Set<string> | null {
		if (a === null && b === null) return null;
		if (a === null) return b;
		if (b === null) return a;
		const out = new Set<string>();
		for (const v of a) if (b.has(v)) out.add(v);
		return out;
	}

	function applyVisualState() {
		if (!svgEl || !payload) return;
		const svg = d3.select(svgEl);
		const links = svg.selectAll('.links path');
		if (links.empty()) return;

		const brancaActive = computeActiveEdges(payload.edges, currentFilters.branca);
		const searchActive = currentSearchTarget
			? computeActiveEdges(payload.edges, [isco1ToNodeId(currentSearchTarget.isco1)])
			: null;
		const pinnedChain = currentPinned ? computeEdgeChain(payload.edges, currentPinned) : null;
		const filterActive = intersect(brancaActive, searchActive);
		// Intersect filter constraints with the click-chain so clicks reveal the
		// full upstream+downstream path while still respecting active filters.
		const activeSet = intersect(filterActive, pinnedChain);
		const metric = currentFilters.colorMetric;

		links
			.transition()
			.duration(220)
			.ease(d3.easeCubicOut)
			.attr('stroke', (d) => {
				const dd = d as unknown as { source: RawNode; target: RawNode; meta: RawEdgeMeta };
				return colorEdge(dd.meta, dd.target, metric);
			})
			.attr('stroke-opacity', (d) => {
				const dd = d as unknown as { source: RawNode; target: RawNode };
				const k = edgeKey({ source: dd.source.id, target: dd.target.id });
				const isPinnedAnchor =
					currentPinned !== null &&
					isSameEdge({ source: dd.source.id, target: dd.target.id }, currentPinned);
				if (isPinnedAnchor) return 0.98;
				if (activeSet === null) return 0.5;
				const isLayered =
					[brancaActive, searchActive, pinnedChain].filter((x) => x !== null).length >= 2;
				return activeSet.has(k) ? (isLayered ? 0.88 : 0.75) : 0.08;
			});

		// Node opacity follows whether any incoming/outgoing edge is active
		if (activeSet) {
			const activeNodeIds = new Set<string>();
			for (const e of payload.edges) {
				const k = `${e.source}__${e.target}`;
				if (activeSet.has(k)) {
					activeNodeIds.add(e.source);
					activeNodeIds.add(e.target);
				}
			}
			svg.selectAll('.nodes g')
				.transition()
				.duration(220)
				.attr('opacity', (d) => (activeNodeIds.has((d as unknown as RawNode).id) ? 1 : 0.35));
		} else {
			svg.selectAll('.nodes g').transition().duration(220).attr('opacity', 1);
		}
	}

	function measureAndRender() {
		if (!containerEl || !payload) return;
		const w = containerEl.clientWidth;
		const h = Math.max(520, Math.min(820, window.innerHeight * 0.72));
		try {
			render(payload, w, h);
		} catch (e) {
			console.error('Sankey render failed:', e);
			status = 'render-error';
			errorMessage = e instanceof Error ? e.message : String(e);
		}
	}

	onMount(() => {
		startDatasets();
		const unsubData = datasets.subscribe((d) => {
			if (d.error) {
				status = 'fetch-error';
				errorMessage = d.error;
				return;
			}
			if (d.sankey) {
				payload = d.sankey as Payload;
				status = 'ready';
				measureAndRender();
			}
		});

		const onResize = () => {
			if (status === 'ready') measureAndRender();
		};
		window.addEventListener('resize', onResize);

		const unsubFilters = filters.subscribe((f) => {
			currentFilters = { gender: f.gender, branca: f.branca, colorMetric: f.colorMetric };
			applyVisualState();
		});
		const unsubSelection = selection.subscribe((s) => {
			currentPinned = s.pinnedEdge;
			currentSearchTarget = s.searchTarget;
			applyVisualState();
		});
		const unsubEaster = easter.subscribe((on) => {
			const changed = easterUnlocked !== on;
			easterUnlocked = on;
			if (changed && status === 'ready') measureAndRender();
		});

		return () => {
			window.removeEventListener('resize', onResize);
			unsubFilters();
			unsubSelection();
			unsubData();
			unsubEaster();
		};
	});
</script>

<div class="sankey-wrap" class:easter-on={easterUnlocked} bind:this={containerEl}>
	{#if easterUnlocked}
		<div class="easter-banner" role="status" aria-live="polite">
			<span class="easter-tag">⌐■_■</span>
			Path desbloquejat: <strong>Negar la pregunta → Revolucionar-se → Felicitat 100</strong>.
			Una broma seriosa: la majoria de joves no estem en cap d'aquests camins, però l'estructura
			ens espera igual. Recarrega la pàgina o lleva <code>?easter=1</code> per amagar-lo.
		</div>
	{/if}
	{#if status === 'loading'}
		<div class="state-skeleton" aria-hidden="true">
			<div class="skel-bar skel-1"></div>
			<div class="skel-bar skel-2"></div>
			<div class="skel-bar skel-3"></div>
			<div class="skel-bar skel-4"></div>
			<div class="skel-bar skel-5"></div>
		</div>
		<p class="state-msg">Carregant l'atles…</p>
	{:else if status === 'fetch-error'}
		<p class="state-msg state-err">
			No s'han pogut carregar les dades del sankey.<br />
			<span class="state-detail">{errorMessage}</span>
		</p>
	{:else if status === 'render-error'}
		<p class="state-msg state-err">
			Error de renderització del sankey.<br />
			<span class="state-detail">{errorMessage}</span>
		</p>
	{/if}

	<svg
		bind:this={svgEl}
		role="img"
		aria-label="Sankey d'itineraris formatius i laborals a Catalunya. Tabula per recórrer les transicions; Enter o Espai per fixar; Esc per desfixar."
	></svg>

	{#if tooltip}
		<div class="tooltip" style="left: {tooltip.x}px; top: {tooltip.y}px;">
			{@html tooltip.html}
		</div>
	{/if}
</div>

<style>
	.sankey-wrap {
		position: relative;
		width: 100%;
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: var(--sp-4);
		overflow: hidden;
	}

	svg {
		display: block;
		width: 100%;
		height: auto;
		min-height: 520px;
	}

	svg :global(.links path:focus-visible) {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}

	svg :global(.links path) {
		outline: none;
	}

	.state-skeleton {
		position: absolute;
		inset: var(--sp-6);
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: var(--sp-4);
		pointer-events: none;
	}

	.skel-bar {
		height: 14px;
		border-radius: var(--radius-pill);
		background: linear-gradient(
			90deg,
			color-mix(in srgb, var(--ink-muted) 14%, transparent),
			color-mix(in srgb, var(--ink-muted) 28%, transparent),
			color-mix(in srgb, var(--ink-muted) 14%, transparent)
		);
		background-size: 200% 100%;
		animation: shimmer 1.6s ease-in-out infinite;
	}

	.skel-1 { width: 76%; }
	.skel-2 { width: 92%; animation-delay: 0.12s; }
	.skel-3 { width: 64%; animation-delay: 0.24s; }
	.skel-4 { width: 85%; animation-delay: 0.36s; }
	.skel-5 { width: 50%; animation-delay: 0.48s; }

	@keyframes shimmer {
		0% { background-position: 0% 0; }
		100% { background-position: 200% 0; }
	}

	.state-msg {
		position: absolute;
		inset: 0;
		display: grid;
		place-items: end center;
		padding-bottom: var(--sp-6);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}

	.state-err {
		color: var(--accent-warm);
		text-align: center;
		padding: var(--sp-4);
	}

	.state-detail {
		display: inline-block;
		margin-top: var(--sp-2);
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}

	.tooltip {
		position: absolute;
		max-width: 320px;
		padding: var(--sp-3) var(--sp-4);
		background: var(--bg-surface);
		color: var(--ink-primary);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		font-size: var(--fs-small);
		line-height: 1.45;
		pointer-events: none;
		z-index: 10;
	}

	.tooltip :global(.num) {
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
	}

	.easter-banner {
		position: relative;
		margin-bottom: var(--sp-3);
		padding: var(--sp-3) var(--sp-4);
		background: linear-gradient(
			90deg,
			color-mix(in srgb, var(--accent-cool) 18%, transparent),
			color-mix(in srgb, var(--accent) 18%, transparent)
		);
		border: 1px dashed color-mix(in srgb, var(--accent) 45%, var(--border-default));
		border-radius: var(--radius-md);
		color: var(--ink-primary);
		font-size: var(--fs-small);
		line-height: 1.5;
	}

	.easter-tag {
		font-family: var(--font-mono);
		color: var(--accent);
		font-weight: 700;
		margin-right: var(--sp-2);
	}

	.easter-banner code {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		padding: 1px 4px;
		border-radius: var(--radius-sm);
		background: var(--bg-base);
		color: var(--ink-secondary);
	}

	.tooltip :global(.src) {
		display: inline-block;
		margin-top: var(--sp-2);
		color: var(--ink-muted);
		font-style: italic;
		font-size: var(--fs-micro);
	}
</style>
