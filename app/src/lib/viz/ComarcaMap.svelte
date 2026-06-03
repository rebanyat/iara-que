<script lang="ts">
	import * as d3 from 'd3';
	import { feature } from 'topojson-client';
	import type { Feature, FeatureCollection, Geometry } from 'geojson';
	import { datasets } from '$lib/stores/data';

	type Metric = 'atur_rate' | 'ocup_rate';

	let containerEl = $state<HTMLDivElement | null>(null);
	let tooltip = $state<{ x: number; y: number; html: string } | null>(null);
	let metric = $state<Metric>('atur_rate');

	const metrics: { id: Metric; label: string; scaleDomain: [number, number]; range: string[] }[] = [
		{
			id: 'atur_rate',
			label: 'taxa d\'atur',
			scaleDomain: [0.04, 0.14],
			range: ['#F8EFD2', '#F2C25D', '#E07C42', '#B53A4C', '#3B1F2B']
		},
		{
			id: 'ocup_rate',
			label: 'taxa d\'ocupació',
			scaleDomain: [0.55, 0.66],
			range: ['#3B1F2B', '#B53A4C', '#E07C42', '#F2C25D', '#F8EFD2']
		}
	];

	const current = $derived(metrics.find((m) => m.id === metric)!);
	const placeholder = $derived(($datasets.comarques?.rows ?? []).some((r) => r.placeholder));

	const fmt = d3.format('.1%');

	type ComarcaProps = { id: string; name: string; provincia: string };

	const features = $derived.by((): FeatureCollection<Geometry, ComarcaProps> | null => {
		const topo = $datasets.comarquesTopo as
			| { objects: Record<string, unknown> }
			| null;
		if (!topo || !topo.objects) return null;
		const firstKey = Object.keys(topo.objects)[0];
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const fc = feature(topo as any, (topo.objects as any)[firstKey]) as unknown as
			| FeatureCollection<Geometry, ComarcaProps>
			| Feature<Geometry, ComarcaProps>;
		// topojson.feature can return Feature or FeatureCollection depending on the
		// input object type; for our 'comarques' object it returns a FeatureCollection.
		if ((fc as FeatureCollection).type === 'FeatureCollection') {
			return fc as FeatureCollection<Geometry, ComarcaProps>;
		}
		return { type: 'FeatureCollection', features: [fc as Feature<Geometry, ComarcaProps>] };
	});

	const metricByComarca = $derived.by(() => {
		const out = new Map<string, number>();
		const rows = $datasets.comarques?.rows ?? [];
		for (const r of rows) out.set(r.name.toLowerCase(), r[metric]);
		return out;
	});

	const color = $derived.by(() => {
		const stops = d3
			.range(current.range.length)
			.map((i) => current.scaleDomain[0] + (i / (current.range.length - 1)) * (current.scaleDomain[1] - current.scaleDomain[0]));
		return d3.scaleLinear<string>().domain(stops).range(current.range).clamp(true);
	});

	type RenderedPath = { name: string; provincia: string; d: string; value: number | undefined };

	const paths = $derived.by((): RenderedPath[] => {
		if (!features) return [];
		const projection = d3.geoMercator().fitSize([480, 320], features);
		const pathGen = d3.geoPath(projection);
		const out: RenderedPath[] = [];
		for (const f of features.features) {
			const name = f.properties.name;
			const d = pathGen(f) ?? '';
			out.push({
				name,
				provincia: f.properties.provincia,
				d,
				value: metricByComarca.get(name.toLowerCase())
			});
		}
		return out;
	});

	function showTooltip(event: MouseEvent, name: string, value: number | undefined) {
		if (value === undefined) return;
		const rect = containerEl?.getBoundingClientRect();
		tooltip = {
			x: event.clientX - (rect?.left ?? 0) + 12,
			y: event.clientY - (rect?.top ?? 0) + 12,
			html: `<strong>${name}</strong><br/>${current.label}: <span class="num">${fmt(value)}</span>`
		};
	}

	function hideTooltip() {
		tooltip = null;
	}
</script>

<div class="map-wrap" bind:this={containerEl}>
	<header>
		<h3>Mapa per comarques</h3>
		<div class="metric-switch" role="radiogroup" aria-label="Mètrica del mapa">
			{#each metrics as m (m.id)}
				<button
					type="button"
					class="m-btn"
					class:active={metric === m.id}
					role="radio"
					aria-checked={metric === m.id}
					onclick={() => (metric = m.id)}
				>
					{m.label}
				</button>
			{/each}
		</div>
	</header>

	{#if paths.length === 0}
		<div class="skel" aria-hidden="true"></div>
		<p class="empty">Carregant comarques…</p>
	{:else}
		<svg viewBox="0 0 480 320" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa coroplètic de Catalunya per comarca">
			<g class="comarques">
				{#each paths as p (p.name)}
					<path
						d={p.d}
						fill={p.value !== undefined ? color(p.value) : '#2a2f3a'}
						stroke="rgba(15,17,21,0.6)"
						stroke-width="0.5"
						role="presentation"
						onmousemove={(event: MouseEvent) => showTooltip(event, p.name, p.value)}
						onmouseleave={hideTooltip}
					></path>
				{/each}
			</g>
		</svg>
	{/if}

	<footer class="legend">
		<span class="num">{fmt(current.scaleDomain[0])}</span>
		<span class="track" style="background: linear-gradient(90deg, {current.range.join(', ')})"></span>
		<span class="num">{fmt(current.scaleDomain[1])}</span>
		{#if placeholder}
			<span class="placeholder-tag" title="dades sintètiques per provincia fins a integrar l'Observatori del Treball">
				placeholder
			</span>
		{/if}
	</footer>

	{#if tooltip}
		<div class="tooltip" style="left: {tooltip.x}px; top: {tooltip.y}px;">
			{@html tooltip.html}
		</div>
	{/if}
</div>

<style>
	.map-wrap {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
		position: relative;
	}

	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--sp-3);
	}

	h3 {
		font-size: 1.05rem;
		font-weight: 700;
	}

	.metric-switch {
		display: flex;
		gap: var(--sp-1);
	}

	.m-btn {
		padding: var(--sp-1) var(--sp-3);
		font-family: var(--font-sans);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-pill);
		transition: background var(--dur-2) var(--ease), color var(--dur-2) var(--ease);
	}

	.m-btn:hover {
		color: var(--ink-primary);
		border-color: var(--border-strong);
	}

	.m-btn.active {
		background: var(--ink-primary);
		color: var(--bg-base);
		border-color: var(--ink-primary);
	}

	svg {
		width: 100%;
		height: auto;
		max-height: 320px;
		background: color-mix(in srgb, var(--bg-base) 70%, transparent);
		border-radius: var(--radius-md);
	}

	.empty {
		color: var(--ink-muted);
		font-size: var(--fs-small);
		font-style: italic;
		padding: var(--sp-3) 0;
	}

	.skel {
		min-height: 200px;
		border-radius: var(--radius-md);
		background:
			radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--accent) 14%, transparent), transparent 55%),
			radial-gradient(circle at 70% 60%, color-mix(in srgb, var(--accent-cool) 14%, transparent), transparent 55%),
			color-mix(in srgb, var(--bg-surface) 92%, transparent);
		border: 1px dashed var(--border-default);
	}

	.legend {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}

	.legend .track {
		flex: 1;
		max-width: 220px;
		height: 8px;
		border-radius: var(--radius-pill);
	}

	.placeholder-tag {
		margin-left: auto;
		padding: 2px var(--sp-2);
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--accent-warm) 22%, transparent);
		color: var(--accent-warm);
		font-style: italic;
	}

	.tooltip {
		position: absolute;
		max-width: 240px;
		padding: var(--sp-2) var(--sp-3);
		background: var(--bg-surface);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		font-size: var(--fs-small);
		line-height: 1.4;
		pointer-events: none;
		z-index: 10;
	}

	.tooltip :global(.num) {
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
	}
</style>
