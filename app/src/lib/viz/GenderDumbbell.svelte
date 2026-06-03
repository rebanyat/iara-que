<script lang="ts">
	import * as d3 from 'd3';
	import { datasets } from '$lib/stores/data';
	import { activeSelection } from '$lib/stores/activeSelection';

	const fmt = d3.format(',');
	const pctFmt = d3.format('.0%');

	type Row = {
		branca: string;
		brancaLabel: string;
		level: 'grau' | 'master' | 'fp_gs' | 'fp_gm' | string;
		salaryF: number;
		salaryM: number;
		gap: number;
		pctFemale: number;
		wave: number;
		source: string;
	};

	const LEVEL_LABEL: Record<string, string> = {
		grau: 'Grau',
		master: 'Màster',
		fp_gs: 'FP-GS',
		fp_gm: 'FP-GM'
	};

	const rows = $derived.by((): Row[] => {
		const data = $datasets;
		const sel = $activeSelection;
		if (!data.genderGap) return [];

		const allowedBranca = new Set<string>(sel.branca);
		const filterByBranca = sel.branca.length > 0;

		// Default: AQU grau only (cleanest comparison). If the user has selected
		// branca filters that don't have AQU grau coverage we fall back to all
		// levels for that branca.
		const out: Row[] = [];
		const seen = new Set<string>();

		const allRows = data.genderGap.rows;
		for (const r of allRows) {
			if (filterByBranca && !allowedBranca.has(r.branca)) continue;
			if (!filterByBranca && r.level !== 'grau') continue;
			const key = `${r.branca}__${r.level}`;
			if (seen.has(key)) continue;
			seen.add(key);
			out.push({
				branca: r.branca,
				brancaLabel: data.genderGap.branca_labels[r.branca] ?? r.branca,
				level: r.level,
				salaryF: r.salary_f,
				salaryM: r.salary_m,
				gap: r.salary_m - r.salary_f,
				pctFemale: r.pct_female,
				wave: r.wave,
				source: r.source
			});
		}

		// Sort by absolute gap descending
		out.sort((a, b) => Math.abs(b.gap) - Math.abs(a.gap));
		return out;
	});

	const xExtent = $derived.by((): [number, number] => {
		if (rows.length === 0) return [16000, 40000];
		const all = rows.flatMap((r) => [r.salaryF, r.salaryM]);
		const min = d3.min(all) ?? 16000;
		const max = d3.max(all) ?? 40000;
		const pad = (max - min) * 0.12 || 2000;
		return [Math.max(0, min - pad), max + pad];
	});

	function xPct(value: number, extent: [number, number]) {
		const [a, b] = extent;
		return ((value - a) / (b - a)) * 100;
	}
</script>

<div class="panel">
	<header>
		<h3>Bretxa salarial per gènere</h3>
		<p class="hint">
			{#if $activeSelection.branca.length > 0}
				branques actives · onada AQU 2023 (FP: Cambres 2022)
			{:else}
				graus universitaris · onada AQU 2023
			{/if}
		</p>
	</header>

	{#if rows.length === 0}
		<p class="empty">Sense dades de bretxa per a aquest subconjunt.</p>
	{:else}
		<ol class="dumbbells" aria-label="Bretxa salarial Dones vs Homes per branca">
			{#each rows as r (r.branca + r.level)}
				<li>
					<div class="row-head">
						<span class="row-label">
							{r.brancaLabel}
							{#if r.level !== 'grau'}<span class="lvl">· {LEVEL_LABEL[r.level] ?? r.level}</span>{/if}
						</span>
						<span class="row-gap" title="bretxa absoluta H − D">
							{r.gap >= 0 ? '+' : ''}<span class="num">{fmt(Math.round(r.gap))}</span> €
						</span>
					</div>
					<div class="track" aria-hidden="true">
						<span
							class="connector"
							style="left: {Math.min(xPct(r.salaryF, xExtent), xPct(r.salaryM, xExtent))}%;
							       width: {Math.abs(xPct(r.salaryM, xExtent) - xPct(r.salaryF, xExtent))}%"
						></span>
						<span class="dot dot-f" style="left: {xPct(r.salaryF, xExtent)}%">
							<span class="dot-label">D</span>
						</span>
						<span class="dot dot-m" style="left: {xPct(r.salaryM, xExtent)}%">
							<span class="dot-label">H</span>
						</span>
					</div>
					<div class="row-meta">
						<span>Dones <span class="num">{fmt(Math.round(r.salaryF))}</span>&nbsp;€</span>
						<span>Homes <span class="num">{fmt(Math.round(r.salaryM))}</span>&nbsp;€</span>
						<span class="muted">% dones {pctFmt(r.pctFemale)}</span>
					</div>
				</li>
			{/each}
		</ol>

		<footer class="axis" aria-hidden="true">
			<span class="num">{fmt(Math.round(xExtent[0]))}&nbsp;€</span>
			<span class="num">{fmt(Math.round(xExtent[1]))}&nbsp;€</span>
		</footer>
	{/if}
</div>

<style>
	.panel {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	header {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: var(--sp-3);
		flex-wrap: wrap;
	}

	h3 {
		font-size: 1.05rem;
		font-weight: 700;
	}

	.hint {
		color: var(--ink-muted);
		font-size: var(--fs-micro);
		font-family: var(--font-mono);
		letter-spacing: 0.04em;
	}

	.empty {
		color: var(--ink-muted);
		font-size: var(--fs-small);
		font-style: italic;
		padding: var(--sp-3) 0;
	}

	.dumbbells {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.dumbbells li {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	.row-head {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: var(--sp-3);
	}

	.row-label {
		font-size: var(--fs-small);
		color: var(--ink-primary);
		font-weight: 500;
	}

	.row-label .lvl {
		color: var(--ink-muted);
		font-weight: 400;
	}

	.row-gap {
		font-size: var(--fs-small);
		color: var(--accent-warm);
	}

	.track {
		position: relative;
		height: 18px;
	}

	.connector {
		position: absolute;
		top: 50%;
		height: 3px;
		transform: translateY(-50%);
		background: color-mix(in srgb, var(--ink-muted) 36%, transparent);
		border-radius: var(--radius-pill);
	}

	.dot {
		position: absolute;
		top: 50%;
		width: 18px;
		height: 18px;
		margin-left: -9px;
		margin-top: -9px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 700;
		color: var(--bg-base);
	}

	.dot-f {
		background: var(--gender-f);
	}

	.dot-m {
		background: var(--gender-m);
	}

	.dot-label {
		pointer-events: none;
	}

	.row-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--sp-3);
		color: var(--ink-secondary);
		font-size: var(--fs-micro);
	}

	.row-meta .muted {
		color: var(--ink-muted);
	}

	.axis {
		display: flex;
		justify-content: space-between;
		color: var(--ink-muted);
		font-size: var(--fs-micro);
		padding-top: var(--sp-2);
		border-top: 1px dashed var(--border-subtle);
	}

	.num {
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
	}
</style>
