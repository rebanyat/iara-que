<script lang="ts">
	import SearchBox from '$lib/ui/SearchBox.svelte';
	import { selection } from '$lib/stores/selection';
	import { datasets } from '$lib/stores/data';
	import { goto } from '$app/navigation';

	type RawEdge = {
		source: string;
		target: string;
		value: number;
		meta: {
			pctEmployed?: number;
			medianSalary?: number;
			pctAdequate?: number;
			composite?: number;
		};
	};

	type RawNode = { id: string; label: string; category: string };

	const target = $derived($selection.searchTarget);
	const sankey = $derived($datasets.sankey as
		| { nodes: RawNode[]; edges: RawEdge[] }
		| undefined);

	const nodeById = $derived.by(() => {
		const m = new Map<string, RawNode>();
		for (const n of sankey?.nodes ?? []) m.set(n.id, n);
		return m;
	});

	function nodeIdForIsco1(isco1: string): string {
		return `isco__${isco1}`;
	}

	// Walk backwards from the ISCO target node through incoming edges and
	// reconstruct the most plausible paths (weighted by edge value). Returns
	// up to 5 paths, each a list of node ids from origin to target.
	const paths = $derived.by(() => {
		if (!target || !sankey) return [] as { nodes: RawNode[]; metrics: RawEdge['meta']; value: number }[];
		const targetId = nodeIdForIsco1(target.isco1);
		if (!nodeById.has(targetId)) return [];

		const incoming = new Map<string, RawEdge[]>();
		for (const e of sankey.edges) {
			(incoming.get(e.target) ?? incoming.set(e.target, []).get(e.target)!).push(e);
		}

		type PartialPath = {
			nodes: string[];
			metric: RawEdge['meta'];
			value: number;
		};
		let frontier: PartialPath[] = [{ nodes: [targetId], metric: {}, value: Infinity }];

		// Walk up to 6 hops back from the target.
		for (let depth = 0; depth < 6; depth++) {
			const next: PartialPath[] = [];
			for (const p of frontier) {
				const last = p.nodes[0];
				const ins = incoming.get(last) ?? [];
				if (ins.length === 0) {
					next.push(p);
					continue;
				}
				// Keep top 3 incoming edges per node to bound the search.
				const sorted = [...ins].sort((a, b) => b.value - a.value).slice(0, 3);
				for (const e of sorted) {
					next.push({
						nodes: [e.source, ...p.nodes],
						metric: p.metric.composite === undefined ? e.meta : p.metric,
						value: Math.min(p.value, e.value)
					});
				}
			}
			frontier = next;
		}

		// Keep only paths that start at an origin node (layer 0 'start__*').
		const final = frontier.filter((p) => p.nodes[0].startsWith('start__'));
		final.sort((a, b) => b.value - a.value);

		const out = final.slice(0, 5).map((p) => ({
			nodes: p.nodes.map((id) => nodeById.get(id)!).filter(Boolean),
			metrics: p.metric,
			value: p.value
		}));
		return out;
	});

	function goToAtlas() {
		if (!target) return;
		const u = new URLSearchParams();
		u.set('target', target.id);
		u.set('isco1', target.isco1);
		goto(`/?${u.toString()}`);
	}

	function pct(x?: number): string {
		if (x === undefined) return '—';
		return new Intl.NumberFormat('ca-ES', { style: 'percent', maximumFractionDigits: 0 }).format(x);
	}

	function eur(x?: number): string {
		if (x === undefined) return '—';
		return new Intl.NumberFormat('ca-ES', { maximumFractionDigits: 0 }).format(x) + ' €';
	}
</script>

<svelte:head>
	<title>Vull ser… — I ara, què?</title>
</svelte:head>

<section class="container intro">
	<p class="eyebrow">Q6 · Explorador d'objectius</p>
	<h1>Vull ser…</h1>
	<p class="lede">
		Escriu una professió i et mostro <strong>els camins documentats</strong> que hi porten
		— branques formatives típiques, mètriques laborals observades a la cohort que ja hi és,
		i una drecera per veure el camí il·luminat dins de l'atles complet.
	</p>

	<div class="search-wrap">
		<SearchBox />
	</div>
</section>

{#if !target}
	<section class="container empty">
		<div class="empty-card">
			<p class="empty-title">Prova: <em>infermer/a</em>, <em>lampista</em>, <em>programador</em>, <em>periodista</em>…</p>
			<p class="empty-sub">
				La cerca conté 3.043 ocupacions ESCO (cobertura europea, etiquetes catalanes per
				als grups ISCO de nivell mitjà-alt) i 20 perfils icònics extrets de Wikidata
				(astronauta, Nobel, etc.) per a aspiracions concretes.
			</p>
			<p class="empty-cta">
				<a href="/" class="btn-ghost">↑ O explora l'atles sense objectiu</a>
			</p>
		</div>
	</section>
{:else}
	<section class="container result" aria-live="polite">
		<header class="result-head">
			<div>
				<p class="eyebrow">Objectiu</p>
				<h2>{target.label}</h2>
				<p class="result-sub">
					{target.iscoLabel}
					{#if target.source === 'wikidata'}
						<span class="badge wd">via Wikidata · il·lustratiu, no estadístic</span>
					{:else}
						<span class="badge esco">ESCO {target.isco1}</span>
					{/if}
				</p>
			</div>
			<button type="button" class="btn-primary" onclick={goToAtlas}>
				Veure il·luminat a l'atles →
			</button>
		</header>

		{#if paths.length === 0}
			<p class="empty-sub">
				No tenim camins agregats per a aquest objectiu encara. Prova un altre títol o
				explora l'atles directament; potser hi ha rastres parcials.
			</p>
		{:else}
			<h3 class="paths-title">Camins típics documentats (top {paths.length})</h3>
			<ol class="paths">
				{#each paths as p, i (i)}
					<li class="path">
						<div class="path-flow">
							{#each p.nodes as n, j (n.id)}
								<span class="step step-{n.category}">{n.label}</span>
								{#if j < p.nodes.length - 1}
									<span class="arr" aria-hidden="true">→</span>
								{/if}
							{/each}
						</div>
						<dl class="path-metrics">
							<div><dt>Ocupació</dt><dd>{pct(p.metrics.pctEmployed)}</dd></div>
							<div><dt>Adequació</dt><dd>{pct(p.metrics.pctAdequate)}</dd></div>
							<div><dt>Salari modal</dt><dd>{eur(p.metrics.medianSalary)}</dd></div>
							<div><dt>Empleabilitat composta</dt>
								<dd>{p.metrics.composite !== undefined ? p.metrics.composite.toFixed(2) : '—'}</dd>
							</div>
						</dl>
					</li>
				{/each}
			</ol>
		{/if}
	</section>
{/if}

<style>
	.intro {
		padding-block: var(--sp-10) var(--sp-6);
		max-width: 880px;
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--ink-muted);
		margin-bottom: var(--sp-3);
	}

	h1 {
		font-size: var(--fs-h1);
	}

	.lede {
		margin-top: var(--sp-4);
		font-size: 1.125rem;
		line-height: var(--lh-loose);
		color: var(--ink-secondary);
		max-width: 60ch;
	}

	.search-wrap {
		margin-top: var(--sp-6);
	}

	.empty {
		padding-block: var(--sp-4) var(--sp-10);
		max-width: 880px;
	}

	.empty-card {
		padding: var(--sp-6);
		border: 1px dashed var(--border-default);
		border-radius: var(--radius-lg);
		background: var(--bg-elev);
	}

	.empty-title {
		font-size: 1.05rem;
		color: var(--ink-primary);
	}

	.empty-title em {
		color: var(--accent);
		font-style: italic;
	}

	.empty-sub {
		margin-top: var(--sp-3);
		color: var(--ink-secondary);
		font-size: var(--fs-small);
		line-height: 1.5;
	}

	.empty-cta {
		margin-top: var(--sp-5);
	}

	.btn-ghost {
		display: inline-block;
		padding: var(--sp-2) var(--sp-4);
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		color: var(--ink-primary);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-pill);
		text-decoration: none;
	}

	.btn-ghost:hover {
		border-color: var(--border-strong);
	}

	.btn-primary {
		padding: var(--sp-2) var(--sp-4);
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		font-weight: 600;
		color: var(--bg-base);
		background: var(--accent);
		border: 1px solid var(--accent);
		border-radius: var(--radius-pill);
		cursor: pointer;
		transition: filter var(--dur-2) var(--ease);
	}

	.btn-primary:hover {
		filter: brightness(1.08);
	}

	.result {
		padding-bottom: var(--sp-10);
		max-width: 1080px;
	}

	.result-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: var(--sp-5);
		flex-wrap: wrap;
		margin-bottom: var(--sp-6);
	}

	.result-head h2 {
		font-size: var(--fs-h2);
		font-family: var(--font-serif);
		line-height: 1.1;
	}

	.result-sub {
		margin-top: var(--sp-2);
		color: var(--ink-muted);
		font-size: var(--fs-small);
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		flex-wrap: wrap;
	}

	.badge {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.05em;
		padding: 2px var(--sp-2);
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-default);
	}

	.badge.wd {
		color: var(--accent-cool);
		border-color: color-mix(in srgb, var(--accent-cool) 35%, var(--border-default));
	}

	.badge.esco {
		color: var(--ink-secondary);
	}

	.paths-title {
		font-size: 1.05rem;
		font-weight: 700;
		margin-bottom: var(--sp-3);
	}

	.paths {
		list-style: none;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.path {
		padding: var(--sp-4) var(--sp-5);
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
	}

	.path-flow {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--sp-2);
		font-size: var(--fs-small);
	}

	.step {
		padding: var(--sp-1) var(--sp-3);
		border-radius: var(--radius-pill);
		border: 1px solid var(--border-default);
		background: var(--bg-base);
		font-weight: 500;
	}

	.step-origin { color: var(--ink-secondary); }
	.step-study { color: var(--accent-cool); border-color: color-mix(in srgb, var(--accent-cool) 30%, var(--border-default)); }
	.step-occupation { color: var(--accent); border-color: color-mix(in srgb, var(--accent) 30%, var(--border-default)); }
	.step-outcome { color: var(--accent-warm); border-color: color-mix(in srgb, var(--accent-warm) 30%, var(--border-default)); }

	.arr {
		color: var(--ink-muted);
		font-family: var(--font-mono);
	}

	.path-metrics {
		margin-top: var(--sp-3);
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: var(--sp-3);
	}

	.path-metrics div {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.path-metrics dt {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		letter-spacing: 0.05em;
	}

	.path-metrics dd {
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
		font-size: 1.05rem;
		color: var(--ink-primary);
		font-weight: 600;
	}
</style>
