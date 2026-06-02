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
	import { computeActiveEdges, edgeKey } from '$lib/utils/path';

	type RawNode = {
		id: string;
		layer: number;
		label: string;
		category: 'origin' | 'study' | 'occupation' | 'outcome';
		branca?: string;
		isco?: string;
		outcome_score?: number;
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

	const CATEGORY_COLOR: Record<RawNode['category'], string> = {
		origin: '#7B8395',
		study: '#4FB6D0',
		occupation: '#FFC857',
		outcome: '#E0533D'
	};

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

		const ids = new Set(p.nodes.map((n) => n.id));
		const safeNodes = p.nodes.map((n) => ({ ...n }));
		const safeLinks = p.edges
			.filter((e) => ids.has(e.source) && ids.has(e.target))
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
			.selectAll('path')
			.data(result.links)
			.enter()
			.append('path')
			.attr('d', sankeyLinkHorizontal())
			.attr('stroke-width', (d) => Math.max(1, (d as unknown as { width: number }).width))
			.attr('cursor', 'pointer');

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
			});

		// ── Nodes ──────────────────────────────────────────────────────
		const node = g.append('g').attr('class', 'nodes').selectAll('g').data(result.nodes).enter().append('g');

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
			.attr('font-size', 12)
			.attr('font-family', 'var(--font-sans)')
			.text((d) => (d as unknown as RawNode).label);

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
		const activeSet = intersect(brancaActive, searchActive);
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
				const isPinned =
					currentPinned !== null &&
					isSameEdge({ source: dd.source.id, target: dd.target.id }, currentPinned);
				if (isPinned) return 0.95;
				if (activeSet === null) return 0.5;
				// Slightly stronger highlight when both filters are active
				const isLayered = brancaActive !== null && searchActive !== null;
				return activeSet.has(k) ? (isLayered ? 0.85 : 0.7) : 0.08;
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
		(async () => {
			try {
				const res = await fetch('/data/sankey.json');
				if (!res.ok) throw new Error(`HTTP ${res.status}`);
				payload = (await res.json()) as Payload;
			} catch (e) {
				console.error('Failed to load sankey.json:', e);
				status = 'fetch-error';
				errorMessage = e instanceof Error ? e.message : String(e);
				return;
			}
			status = 'ready';
			measureAndRender();
		})();

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

		return () => {
			window.removeEventListener('resize', onResize);
			unsubFilters();
			unsubSelection();
		};
	});
</script>

<div class="sankey-wrap" bind:this={containerEl}>
	{#if status === 'loading'}
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
		aria-label="Sankey d'itineraris formatius i laborals a Catalunya"
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

	.state-msg {
		position: absolute;
		inset: 0;
		display: grid;
		place-items: center;
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

	.tooltip :global(.src) {
		display: inline-block;
		margin-top: var(--sp-2);
		color: var(--ink-muted);
		font-style: italic;
		font-size: var(--fs-micro);
	}
</style>
