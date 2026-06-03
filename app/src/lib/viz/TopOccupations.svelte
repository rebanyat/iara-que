<script lang="ts">
	import * as d3 from 'd3';
	import { datasets, type SankeyEdge } from '$lib/stores/data';
	import { activeSelection } from '$lib/stores/activeSelection';
	import { isco1ToNodeId } from '$lib/stores/selection';
	import { computeActiveEdges } from '$lib/utils/path';

	const ISCO_LABEL: Record<string, string> = {
		isco__1: 'Directius i gerents',
		isco__2: 'Professionals científics',
		isco__3: 'Tècnics i suport',
		isco__4: 'Administratius',
		isco__5: 'Serveis i venda',
		isco__6: 'Agricultura i pesca',
		isco__7: 'Artesans i oficis',
		isco__8: 'Operadors d\'instal·lacions',
		isco__9: 'Ocupacions elementals'
	};

	const fmt = d3.format(',');
	const pctFmt = d3.format('.0%');

	type Row = {
		id: string;
		label: string;
		value: number;
		share: number;
		bestSalary: number | null;
		bestEmployed: number | null;
		composite: number | null;
	};

	const rows = $derived.by((): Row[] => {
		const data = $datasets;
		const sel = $activeSelection;
		if (!data.sankey) return [];

		// 1. Active set
		const brancaActive = computeActiveEdges(data.sankey.edges as SankeyEdge[], sel.branca);
		const searchActive = sel.searchTarget
			? computeActiveEdges(data.sankey.edges as SankeyEdge[], [isco1ToNodeId(sel.searchTarget.isco1)])
			: null;
		let active: Set<string> | null;
		if (brancaActive === null && searchActive === null) active = null;
		else if (brancaActive === null) active = searchActive;
		else if (searchActive === null) active = brancaActive;
		else {
			active = new Set<string>();
			for (const v of brancaActive) if (searchActive.has(v)) active.add(v);
		}

		// 2. Sum edge values into ISCO targets
		const agg = new Map<string, { value: number; meta: { salary: number[]; employed: number[]; composite: number[] } }>();
		for (const e of data.sankey.edges) {
			if (!e.target.startsWith('isco__')) continue;
			const key = `${e.source}__${e.target}`;
			if (active !== null && !active.has(key)) continue;
			const cur = agg.get(e.target) ?? { value: 0, meta: { salary: [], employed: [], composite: [] } };
			cur.value += e.value;
			if (typeof e.meta.medianSalary === 'number') cur.meta.salary.push(e.meta.medianSalary);
			if (typeof e.meta.pctEmployed === 'number') cur.meta.employed.push(e.meta.pctEmployed);
			if (typeof e.meta.composite === 'number') cur.meta.composite.push(e.meta.composite);
			agg.set(e.target, cur);
		}

		const total = Array.from(agg.values()).reduce((s, r) => s + r.value, 0);
		const result: Row[] = Array.from(agg.entries())
			.map(([id, cur]) => {
				const bestSalary = cur.meta.salary.length
					? Math.max(...cur.meta.salary)
					: null;
				const bestEmployed = cur.meta.employed.length ? Math.max(...cur.meta.employed) : null;
				const composite = cur.meta.composite.length ? d3.mean(cur.meta.composite) ?? null : null;
				return {
					id,
					label: ISCO_LABEL[id] ?? id,
					value: cur.value,
					share: total > 0 ? cur.value / total : 0,
					bestSalary,
					bestEmployed,
					composite
				};
			})
			.sort((a, b) => b.value - a.value);

		return result;
	});

	const maxValue = $derived.by(() => (rows.length > 0 ? rows[0].value : 1));
</script>

<div class="panel">
	<header>
		<h3>Top sortides ocupacionals</h3>
		<p class="hint">
			{#if $activeSelection.pathMode}
				volums agregats <em>només per al subconjunt actiu</em>
			{:else}
				volums agregats al total de l'atles
			{/if}
		</p>
	</header>

	{#if rows.length === 0}
		<p class="empty">No hi ha cap camí actiu amb aquesta combinació de filtres.</p>
	{:else}
		<ol class="bars" aria-label="Top ocupacions per volum del camí actiu">
			{#each rows as r (r.id)}
				<li>
					<div class="row-head">
						<span class="row-label">{r.label}</span>
						<span class="row-num"><span class="num">{fmt(r.value)}</span></span>
					</div>
					<div class="row-bar" aria-hidden="true">
						<span class="row-fill" style="width: {(100 * r.value) / maxValue}%"></span>
					</div>
					<div class="row-meta">
						{#if r.composite !== null}
							<span title="empleabilitat composta mitjana de les arestes que hi arriben">
								empleabilitat <span class="num">{r.composite.toFixed(2)}</span>
							</span>
						{/if}
						{#if r.bestEmployed !== null}
							<span title="taxa d'ocupació de la millor branca dins d'aquesta ocupació">
								millor ocupats {pctFmt(r.bestEmployed)}
							</span>
						{/if}
						{#if r.bestSalary !== null}
							<span title="salari modal de la millor branca dins d'aquesta ocupació">
								fins a <span class="num">{fmt(r.bestSalary)}</span>&nbsp;€
							</span>
						{/if}
					</div>
				</li>
			{/each}
		</ol>
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

	.hint em {
		font-style: italic;
		color: var(--accent);
		font-weight: 600;
	}

	.empty {
		color: var(--ink-muted);
		font-size: var(--fs-small);
		font-style: italic;
		padding: var(--sp-3) 0;
	}

	.bars {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}

	.bars li {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
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

	.row-num {
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		flex-shrink: 0;
	}

	.row-bar {
		position: relative;
		height: 8px;
		background: color-mix(in srgb, var(--ink-muted) 22%, transparent);
		border-radius: var(--radius-pill);
		overflow: hidden;
	}

	.row-fill {
		position: absolute;
		inset: 0 auto 0 0;
		background: linear-gradient(90deg, #e07c42, #f2c25d);
		border-radius: var(--radius-pill);
		transition: width var(--dur-3) var(--ease);
	}

	.row-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--sp-3);
		color: var(--ink-muted);
		font-size: var(--fs-micro);
	}

	.num {
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
	}
</style>
