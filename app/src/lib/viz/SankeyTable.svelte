<script lang="ts">
	import * as d3 from 'd3';
	import { datasets, type SankeyEdge } from '$lib/stores/data';
	import { activeSelection } from '$lib/stores/activeSelection';
	import { isco1ToNodeId } from '$lib/stores/selection';
	import { computeActiveEdges } from '$lib/utils/path';

	const integerFormat = d3.format(',');
	const pctFormat = d3.format('.0%');

	type Row = {
		source: string;
		target: string;
		value: number;
		pct?: number;
		salary?: number;
		employed?: number;
		adequate?: number;
		composite?: number;
		wave?: number;
		sourceDataset: string;
		placeholder: boolean;
	};

	const rows = $derived.by((): Row[] => {
		const data = $datasets;
		if (!data.sankey) return [];

		const sel = $activeSelection;
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

		const idToLabel = new Map(data.sankey.nodes.map((n) => [n.id, n.label]));
		const out: Row[] = [];
		for (const e of data.sankey.edges) {
			if (active !== null && !active.has(`${e.source}__${e.target}`)) continue;
			out.push({
				source: idToLabel.get(e.source) ?? e.source,
				target: idToLabel.get(e.target) ?? e.target,
				value: e.value,
				pct: e.meta.pctOfSource,
				salary: e.meta.medianSalary,
				employed: e.meta.pctEmployed,
				adequate: e.meta.pctAdequate,
				composite: e.meta.composite,
				wave: e.meta.wave,
				sourceDataset: e.meta.sourceDataset,
				placeholder: !!e.meta.placeholder
			});
		}
		out.sort((a, b) => b.value - a.value);
		return out;
	});
</script>

<section class="table-view">
	<header>
		<h2>Vista en taula</h2>
		<p>
			Llistat de totes les transicions actives del sankey, ordenades per volum.
			Aquesta vista alternativa, compatible amb lectors de pantalla, està disponible
			als enllaços <code>?view=table</code> de qualsevol estat de filtre.
		</p>
	</header>

	{#if rows.length === 0}
		<p class="empty">No hi ha transicions actives en aquest subconjunt.</p>
	{:else}
		<div class="table-scroll">
			<table>
				<caption class="sr-only">Transicions del sankey amb les seves mètriques</caption>
				<thead>
					<tr>
						<th scope="col">Des de</th>
						<th scope="col">Cap a</th>
						<th scope="col" class="num">Volum</th>
						<th scope="col" class="num">% origen</th>
						<th scope="col" class="num">Ocupats</th>
						<th scope="col" class="num">Adequació</th>
						<th scope="col" class="num">Salari modal</th>
						<th scope="col" class="num">Empleab. composta</th>
						<th scope="col">Font</th>
					</tr>
				</thead>
				<tbody>
					{#each rows as r, i (i)}
						<tr class:placeholder={r.placeholder}>
							<th scope="row">{r.source}</th>
							<td>{r.target}</td>
							<td class="num">{integerFormat(r.value)}</td>
							<td class="num">{r.pct !== undefined ? pctFormat(r.pct) : '—'}</td>
							<td class="num">{r.employed !== undefined ? pctFormat(r.employed) : '—'}</td>
							<td class="num">{r.adequate !== undefined ? pctFormat(r.adequate) : '—'}</td>
							<td class="num">{r.salary !== undefined ? integerFormat(Math.round(r.salary)) + ' €' : '—'}</td>
							<td class="num">{r.composite !== undefined ? r.composite.toFixed(2) : '—'}</td>
							<td class="src">
								{r.sourceDataset}
								{#if r.wave}· {r.wave}{/if}
								{#if r.placeholder}<span class="tag">estimació</span>{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</section>

<style>
	.table-view {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		margin-top: var(--sp-6);
	}

	header h2 {
		font-size: var(--fs-h2);
		font-weight: 700;
	}

	header p {
		margin-top: var(--sp-3);
		max-width: 60ch;
		color: var(--ink-secondary);
	}

	header code {
		background: var(--bg-elev);
		padding: 0 var(--sp-1);
		border-radius: var(--radius-sm);
		font-size: 0.95em;
	}

	.empty {
		color: var(--ink-muted);
		font-style: italic;
	}

	.table-scroll {
		overflow-x: auto;
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--fs-small);
	}

	thead th {
		text-align: left;
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--ink-muted);
		padding: var(--sp-3) var(--sp-3);
		background: var(--bg-elev);
		border-bottom: 1px solid var(--border-default);
		white-space: nowrap;
	}

	tbody th,
	tbody td {
		padding: var(--sp-2) var(--sp-3);
		border-bottom: 1px solid var(--border-subtle);
		color: var(--ink-secondary);
	}

	tbody th {
		font-weight: 500;
		text-align: left;
		color: var(--ink-primary);
	}

	tbody tr:hover {
		background: color-mix(in srgb, var(--accent) 6%, transparent);
	}

	.num {
		text-align: right;
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
		white-space: nowrap;
	}

	.src {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		white-space: nowrap;
	}

	.tag {
		display: inline-block;
		margin-left: var(--sp-2);
		padding: 0 var(--sp-2);
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--accent-warm) 22%, transparent);
		color: var(--accent-warm);
		font-style: italic;
	}

	tr.placeholder td,
	tr.placeholder th {
		color: var(--ink-muted);
	}
</style>
