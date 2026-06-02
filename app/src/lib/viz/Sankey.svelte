<script lang="ts">
	import { onMount } from 'svelte';
	import { sankey as d3Sankey, sankeyLinkHorizontal, sankeyLeft } from 'd3-sankey';
	import * as d3 from 'd3';

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
		pctEmployed?: number;
		pctAdequate?: number;
		medianMonthsToJob?: number;
		genderRatio?: { F: number; M: number };
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
	};

	let svgEl = $state<SVGSVGElement | null>(null);
	let containerEl = $state<HTMLDivElement | null>(null);
	let tooltip = $state<{ x: number; y: number; html: string } | null>(null);
	let status = $state<'loading' | 'ready' | 'error'>('loading');
	let payload = $state<Payload | null>(null);

	const CATEGORY_COLOR: Record<RawNode['category'], string> = {
		origin: '#7B8395',
		study: '#4FB6D0',
		occupation: '#FFC857',
		outcome: '#E0533D'
	};

	const integerFormat = d3.format(',');
	const pctFormat = d3.format('.0%');
	const salaryFormat = (n: number) => integerFormat(Math.round(n)) + ' €';

	function colorEdge(d: { source: { category?: string }; target: RawNode & { outcome_score?: number } }): string {
		const scale = d3
			.scaleLinear<string>()
			.domain([0, 0.3, 0.6, 0.9])
			.range(['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D'])
			.clamp(true);
		const score = d.target?.outcome_score;
		if (typeof score === 'number') return scale(score);
		const cat = d.target?.category;
		if (cat && CATEGORY_COLOR[cat as RawNode['category']]) return CATEGORY_COLOR[cat as RawNode['category']];
		return '#7B8395';
	}

	function render(p: Payload, width: number, height: number) {
		if (!svgEl) return;
		const svg = d3.select(svgEl);
		svg.selectAll('*').remove();

		const idToIdx = new Map(p.nodes.map((n, i) => [n.id, i]));
		const graph = {
			nodes: p.nodes.map((n) => ({ ...n })),
			links: p.edges
				.map((e) => {
					const s = idToIdx.get(e.source);
					const t = idToIdx.get(e.target);
					if (s === undefined || t === undefined) return null;
					return { source: s, target: t, value: e.value, meta: e.meta };
				})
				.filter((e): e is { source: number; target: number; value: number; meta: RawEdgeMeta } => e !== null)
		};

		const margin = { top: 20, right: 240, bottom: 20, left: 20 };
		const innerW = Math.max(640, width - margin.left - margin.right);
		const innerH = Math.max(420, height - margin.top - margin.bottom);

		const layout = d3Sankey<{ id: string; label: string; category: string; layer: number }, { value: number; meta: RawEdgeMeta }>()
			.nodeId((d) => (d as unknown as { id: string }).id)
			.nodeAlign(sankeyLeft)
			.nodeWidth(14)
			.nodePadding(14)
			.extent([
				[1, 1],
				[innerW, innerH]
			]);

		// d3-sankey mutates the input; cast through unknown to satisfy the generics
		const result = layout({
			nodes: graph.nodes.map((n) => ({ ...n })) as never,
			links: graph.links.map((l) => ({ ...l })) as never
		});

		svg
			.attr('viewBox', `0 0 ${innerW + margin.left + margin.right} ${innerH + margin.top + margin.bottom}`)
			.attr('preserveAspectRatio', 'xMidYMid meet');

		const g = svg
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Links
		const link = g
			.append('g')
			.attr('fill', 'none')
			.attr('stroke-opacity', 0.45)
			.selectAll('path')
			.data(result.links)
			.enter()
			.append('path')
			.attr('d', sankeyLinkHorizontal())
			.attr('stroke', (d) => colorEdge(d as never))
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
				const bits: string[] = [];
				bits.push(`<strong>${dd.source.label}</strong> → <strong>${dd.target.label}</strong>`);
				bits.push(`Volum: <span class="num">${integerFormat(dd.value)}</span>`);
				if (dd.meta.pctOfSource !== undefined) bits.push(`% origen: ${pctFormat(dd.meta.pctOfSource)}`);
				if (dd.meta.medianSalary !== undefined) bits.push(`Salari medià: ${salaryFormat(dd.meta.medianSalary)}`);
				if (dd.meta.pctEmployed !== undefined) bits.push(`Ocupats: ${pctFormat(dd.meta.pctEmployed)}`);
				if (dd.meta.pctAdequate !== undefined) bits.push(`Adequació: ${pctFormat(dd.meta.pctAdequate)}`);
				if (dd.meta.medianMonthsToJob !== undefined) bits.push(`Mesos a feina: ${dd.meta.medianMonthsToJob}`);
				if (dd.meta.genderRatio)
					bits.push(`Gènere: F ${pctFormat(dd.meta.genderRatio.F)} · M ${pctFormat(dd.meta.genderRatio.M)}`);
				if (dd.meta.sourceDataset) bits.push(`<em class="src">font: ${dd.meta.sourceDataset}${dd.meta.placeholder ? ' (placeholder)' : ''}</em>`);
				const rect = containerEl?.getBoundingClientRect();
				tooltip = {
					x: event.clientX - (rect?.left ?? 0) + 14,
					y: event.clientY - (rect?.top ?? 0) + 14,
					html: bits.join('<br/>')
				};
			})
			.on('mouseleave', () => {
				tooltip = null;
			});

		// Nodes
		const node = g
			.append('g')
			.selectAll('g')
			.data(result.nodes)
			.enter()
			.append('g');

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
	}

	function measureAndRender() {
		if (!containerEl || !payload) return;
		const w = containerEl.clientWidth;
		const h = Math.max(520, Math.min(820, window.innerHeight * 0.72));
		render(payload, w, h);
	}

	onMount(() => {
		(async () => {
			try {
				const res = await fetch('/data/sankey.json');
				if (!res.ok) throw new Error(`HTTP ${res.status}`);
				payload = (await res.json()) as Payload;
				status = 'ready';
				measureAndRender();
			} catch (e) {
				console.error('Failed to load sankey.json:', e);
				status = 'error';
			}
		})();

		const onResize = () => measureAndRender();
		window.addEventListener('resize', onResize);
		return () => window.removeEventListener('resize', onResize);
	});
</script>

<div class="sankey-wrap" bind:this={containerEl}>
	{#if status === 'loading'}
		<p class="state-msg">Carregant l'atles…</p>
	{:else if status === 'error'}
		<p class="state-msg state-err">No s'han pogut carregar les dades del sankey.</p>
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

	{#if payload}
		<div class="legend" aria-hidden="true">
			<span class="dot" style="background: {CATEGORY_COLOR.origin}"></span> origen
			<span class="dot" style="background: {CATEGORY_COLOR.study}"></span> formació
			<span class="dot" style="background: {CATEGORY_COLOR.occupation}"></span> ocupació
			<span class="dot" style="background: {CATEGORY_COLOR.outcome}"></span> outcome
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

	.legend {
		display: flex;
		gap: var(--sp-4);
		flex-wrap: wrap;
		margin-top: var(--sp-3);
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		font-family: var(--font-mono);
	}

	.dot {
		display: inline-block;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		margin-right: 6px;
		vertical-align: -1px;
	}
</style>
