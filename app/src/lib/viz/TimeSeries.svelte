<script lang="ts">
	import * as d3 from 'd3';
	import { datasets, type TimeSeriesPoint } from '$lib/stores/data';
	import { activeSelection } from '$lib/stores/activeSelection';

	const BRANCA_COLOR: Record<string, string> = {
		branca__stem: '#4FB6D0',
		branca__health: '#C16BA1',
		branca__social: '#FFC857',
		branca__hum: '#8FB17A',
		branca__services: '#E07C42',
		branca__industry: '#5B8FB9'
	};

	type Metric = 'composite_employability' | 'pct_employed' | 'salary_modal';

	let metric = $state<Metric>('composite_employability');

	const fmt = d3.format(',');
	const pctFmt = d3.format('.0%');

	const metrics: { id: Metric; label: string }[] = [
		{ id: 'composite_employability', label: 'empleabilitat composta' },
		{ id: 'pct_employed', label: '% ocupats' },
		{ id: 'salary_modal', label: 'salari modal' }
	];

	const series = $derived.by(() => $datasets.timeSeries?.series ?? []);
	const labels = $derived.by(() => $datasets.timeSeries?.branca_labels ?? {});
	const activeBranca = $derived.by(() => new Set<string>($activeSelection.branca));

	const yExtent = $derived.by((): [number, number] => {
		const values = series.flatMap((s) => s.points.map((p) => p[metric]));
		if (values.length === 0) return [0, 1];
		const min = d3.min(values) ?? 0;
		const max = d3.max(values) ?? 1;
		const pad = (max - min) * 0.12 || 0.05;
		return [Math.max(0, min - pad), max + pad];
	});

	const xValues = $derived.by(() => [2014, 2017, 2020, 2023]);
	const xScale = (year: number) => 24 + ((year - 2014) / (2023 - 2014)) * 412;
	const yScale = (v: number) => {
		const [lo, hi] = yExtent;
		const t = (v - lo) / (hi - lo);
		return 200 - t * 170;
	};

	function lineFor(points: TimeSeriesPoint[]): string {
		return points
			.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(p.wave)} ${yScale(p[metric])}`)
			.join(' ');
	}

	function formatMetric(v: number): string {
		if (metric === 'salary_modal') return `${fmt(Math.round(v))} €`;
		return pctFmt(v);
	}
</script>

<div class="ts-wrap">
	<header>
		<h3>Evolució 2014 → 2023</h3>
		<div class="metric-switch" role="radiogroup" aria-label="Mètrica de la sèrie temporal">
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

	{#if series.length === 0}
		<p class="empty">Carregant sèries temporals…</p>
	{:else}
		<svg viewBox="0 0 460 230" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Línies temporals d'empleabilitat per branca">
			<!-- Y gridlines -->
			{#each d3.ticks(yExtent[0], yExtent[1], 4) as t (t)}
				<g class="grid">
					<line x1="24" x2="436" y1={yScale(t)} y2={yScale(t)} />
					<text x="20" y={yScale(t)} text-anchor="end" dominant-baseline="middle">{formatMetric(t)}</text>
				</g>
			{/each}

			<!-- X axis labels -->
			{#each xValues as x (x)}
				<text class="axis-x" x={xScale(x)} y={222} text-anchor="middle">{x}</text>
			{/each}

			<!-- Lines -->
			{#each series as s (s.branca)}
				{@const active = activeBranca.size === 0 || activeBranca.has(s.branca)}
				<path
					d={lineFor(s.points)}
					fill="none"
					stroke={BRANCA_COLOR[s.branca] ?? '#888'}
					stroke-width={active ? 2.2 : 1.2}
					stroke-opacity={active ? 0.95 : 0.32}
					stroke-linecap="round"
					stroke-linejoin="round"
				></path>
				{#each s.points as p (p.wave)}
					<circle
						cx={xScale(p.wave)}
						cy={yScale(p[metric])}
						r={active ? 3.5 : 2}
						fill={BRANCA_COLOR[s.branca] ?? '#888'}
						opacity={active ? 1 : 0.3}
					>
						<title>{labels[s.branca] ?? s.branca} · {p.wave} · {formatMetric(p[metric])}</title>
					</circle>
				{/each}
				{@const last = s.points[s.points.length - 1]}
				<text
					class="label"
					x={xScale(last.wave) + 6}
					y={yScale(last[metric])}
					dominant-baseline="middle"
					fill={BRANCA_COLOR[s.branca] ?? '#888'}
					opacity={active ? 1 : 0.4}
				>
					{labels[s.branca]?.split(' ')[0] ?? s.branca}
				</text>
			{/each}
		</svg>

		<p class="hint">
			{activeBranca.size > 0
				? 'Línies destacades: branques al filtre. La resta resten al context.'
				: 'Quatre onades AQU (graus universitaris). Filtra una branca per fer focus.'}
		</p>
	{/if}
</div>

<style>
	.ts-wrap {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
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

	.empty {
		color: var(--ink-muted);
		font-size: var(--fs-small);
		font-style: italic;
	}

	svg {
		width: 100%;
		height: auto;
		max-height: 240px;
		background: color-mix(in srgb, var(--bg-base) 70%, transparent);
		border-radius: var(--radius-md);
	}

	.grid line {
		stroke: var(--border-subtle);
		stroke-width: 1;
		stroke-dasharray: 2 4;
	}

	.grid text {
		font-family: var(--font-mono);
		font-size: 9px;
		fill: var(--ink-muted);
	}

	.axis-x {
		font-family: var(--font-mono);
		font-size: 10px;
		fill: var(--ink-muted);
	}

	.label {
		font-family: var(--font-sans);
		font-size: 10px;
		font-weight: 600;
	}

	.hint {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		margin-top: var(--sp-1);
	}
</style>
