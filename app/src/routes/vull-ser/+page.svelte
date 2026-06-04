<script lang="ts">
	import SearchBox from '$lib/ui/SearchBox.svelte';
	import { selection, clearSearchTarget } from '$lib/stores/selection';
	import {
		datasets,
		type StartingPoint,
		type LifeGoal,
		type Resource
	} from '$lib/stores/data';
	import { optimisePath, goalToTarget, type PlanPath } from '$lib/utils/planner';

	let selectedStart = $state<StartingPoint | null>(null);
	let startQuery = $state<string>('');
	let showStartList = $state<boolean>(false);

	let selectedGoal = $state<LifeGoal | null>(null);

	const startingPoints = $derived($datasets.startingPoints?.points ?? []);
	const lifeGoals = $derived($datasets.lifeGoals?.goals ?? []);
	const allResources = $derived($datasets.resources?.resources ?? []);
	const sankey = $derived($datasets.sankey);
	const escoTarget = $derived($selection.searchTarget);

	const filteredStarts = $derived.by(() => {
		const q = startQuery.trim().toLowerCase();
		if (!q) return startingPoints.slice(0, 10);
		return startingPoints.filter((p) => p.label.toLowerCase().includes(q)).slice(0, 12);
	});

	const stageLabels: Record<string, string> = {
		eso: 'ESO',
		batx: 'Batxillerat',
		fp_gm: 'FP-GM',
		fp_gs: 'FP-GS',
		grau: 'Grau',
		working: 'Treballant',
		reorient: 'Reorientació'
	};

	function pickStart(p: StartingPoint) {
		selectedStart = p;
		startQuery = p.label;
		showStartList = false;
	}

	function clearStart() {
		selectedStart = null;
		startQuery = '';
	}

	function pickGoal(g: LifeGoal) {
		selectedGoal = g;
		clearSearchTarget(); // life-goal and ESCO target are mutually exclusive
	}

	function clearGoal() {
		selectedGoal = null;
	}

	// Compute plans whenever both start and target are set.
	const plans = $derived.by((): PlanPath[] => {
		if (!sankey || !selectedStart) return [];
		// Always plan from the parent sankey node; the child_node (titul__*)
		// is shown only as context in the UI because it has no outgoing
		// edges in the static sankey (children are dynamic expansions).
		const fromNode = selectedStart.node;

		if (selectedGoal) {
			const tgt = goalToTarget(selectedGoal);
			return optimisePath(
				{
					fromNode,
					targetIsco1: tgt.targetIsco1,
					targetBrancas: tgt.targetBrancas,
					preferences: tgt.preferences
				},
				sankey.nodes,
				sankey.edges
			);
		}

		if (escoTarget) {
			return optimisePath(
				{
					fromNode,
					targetIsco1: [escoTarget.isco1],
					targetBrancas: []
				},
				sankey.nodes,
				sankey.edges
			);
		}

		return [];
	});

	const ready = $derived(selectedStart !== null && (selectedGoal !== null || escoTarget !== null));

	// Stage-aware resources: filter by stage of the starting point + branca hint.
	const stageResources = $derived.by((): Record<string, Resource[]> => {
		if (!selectedStart) return {};
		const stage = selectedStart.stage;
		const brancaHints = new Set<string>();
		if (selectedStart.branca_hint) brancaHints.add(selectedStart.branca_hint);
		if (selectedGoal) for (const b of selectedGoal.branca) brancaHints.add(b);

		const matches = allResources.filter((r) => {
			if (!r.stage.includes(stage)) return false;
			if (r.branca.length === 0) return true; // cross-cutting
			if (brancaHints.size === 0) return true;
			return r.branca.some((b) => brancaHints.has(b));
		});

		const grouped: Record<string, Resource[]> = {};
		const order: Array<Resource['type']> = ['orientacio', 'uni', 'fp', 'beca', 'idiomes', 'plataforma', 'emprenedoria', 'sindicat'];
		for (const t of order) grouped[t] = matches.filter((r) => r.type === t).slice(0, 5);
		return grouped;
	});

	const groupLabels: Record<Resource['type'], string> = {
		uni: 'Universitats',
		fp: 'Centres FP de referència',
		beca: 'Beques i ajuts',
		orientacio: 'Orientació personalitzada',
		plataforma: 'Plataformes online',
		sindicat: 'Sindicats i drets',
		emprenedoria: 'Emprenedoria',
		idiomes: 'Idiomes'
	};

	function eur(x?: number): string {
		if (x === undefined) return '—';
		return new Intl.NumberFormat('ca-ES', { maximumFractionDigits: 0 }).format(x) + ' €';
	}

	function pct(x?: number): string {
		if (x === undefined) return '—';
		return new Intl.NumberFormat('ca-ES', { style: 'percent', maximumFractionDigits: 0 }).format(x);
	}

	function categoryClass(c: string): string {
		return `step-${c}`;
	}
</script>

<svelte:head>
	<title>Vull ser… — Planificador · I ara, què?</title>
</svelte:head>

<section class="container intro">
	<p class="eyebrow">Planificador · explora itineraris</p>
	<h1><em>I ara…</em> què?</h1>
	<p class="lede">
		Tria <strong>on ets ara</strong> i <strong>cap a on vols anar</strong>. Et calculo els
		camins documentats més òptims a partir de les dades agregades de l'atles i et
		suggereixo recursos públics concrets per a cada etapa. Pots triar un objectiu concret
		(metge, lampista, youtuber…) o un objectiu vital (tenir un negoci propi, salari alt,
		viure de l'art…).
	</p>
</section>

<section class="container wizard">
	<div class="step-card" class:complete={selectedStart !== null}>
		<header>
			<span class="step-num">1</span>
			<h2><em>I ara…</em></h2>
		</header>
		<p class="step-sub">Què estàs fent en aquest moment de la teva vida formativa o laboral?</p>
		<div class="start-box">
			<input
				type="text"
				placeholder="Escriu o tria de la llista (p. ex. «grau de matemàtiques», «FP-GM informàtica», «treballo a serveis»)"
				bind:value={startQuery}
				oninput={() => (showStartList = true)}
				onfocus={() => (showStartList = true)}
				onblur={() => setTimeout(() => (showStartList = false), 150)}
			/>
			{#if selectedStart}
				<button type="button" class="clear-btn" onclick={clearStart}>×</button>
			{/if}
			{#if showStartList && filteredStarts.length > 0}
				<ul class="start-list" role="listbox">
					{#each filteredStarts as p (p.id)}
						<li>
							<button type="button" onmousedown={(e) => { e.preventDefault(); pickStart(p); }}>
								<span class="start-label">{p.label}</span>
								<span class="start-meta">{stageLabels[p.stage] ?? p.stage}{p.branca_hint ? ' · ' + p.branca_hint.replace('branca__', '') : ''}</span>
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
		{#if selectedStart?.blurb}
			<p class="hint">{selectedStart.blurb}</p>
		{/if}
	</div>

	<div class="step-card" class:complete={selectedGoal !== null || escoTarget !== null}>
		<header>
			<span class="step-num">2</span>
			<h2><em>què?</em></h2>
		</header>
		<p class="step-sub">Cap a on vols anar — pot ser un ofici concret o un objectiu vital.</p>

		<p class="sub-hint">Oficis concrets (metge, lampista, youtuber, sumiller…)</p>
		<div class="esco-wrap">
			<SearchBox />
		</div>

		<p class="sub-hint">Objectius vitals (desplaça per veure'ls tots)</p>
		<div class="goals-scroll">
			<div class="goals-grid">
				{#each lifeGoals as g (g.id)}
					<button
						type="button"
						class="goal-card"
						class:active={selectedGoal?.id === g.id}
						onclick={() => pickGoal(g)}
					>
						<span class="goal-label">{g.label}</span>
						<span class="goal-blurb">{g.blurb}</span>
					</button>
				{/each}
			</div>
		</div>

		{#if selectedGoal}
			<div class="goal-detail">
				<header>
					<strong>{selectedGoal.label}</strong>
					<button type="button" class="clear-btn" onclick={clearGoal}>×</button>
				</header>
				{#if selectedGoal.exemplars}
					<p class="goal-exempl">Exemples: {selectedGoal.exemplars.join(' · ')}</p>
				{/if}
				{#if selectedGoal.honestly}
					<p class="goal-honest">{selectedGoal.honestly}</p>
				{/if}
			</div>
		{/if}
	</div>
</section>

{#if ready}
	<section class="container plans" aria-live="polite">
		<header class="plans-head">
			<h2>{plans.length > 0 ? `${plans.length} camí${plans.length > 1 ? 's' : ''} compatible${plans.length > 1 ? 's' : ''}` : 'Camins documentats'}</h2>
			{#if selectedStart?.child_node}
				<p class="hint">
					Tens un camí ja concret (<strong>{selectedStart.label}</strong>). Els resultats
					mostren els passos que et queden a partir d'on ets ara dins de la branca.
				</p>
			{/if}
			{#if plans.length === 0}
				<p class="empty">
					No hi ha camins documentats agregats que enllacin la teva situació amb aquest
					objectiu dins de l'atles. Això no vol dir que sigui impossible — sovint és el
					contrari: vol dir que la mostra estadística és prima. Demana cita amb un
					orientador del SOC.
				</p>
			{/if}
		</header>

		{#if plans.length > 0}
			<ol class="plan-list">
				{#each plans as p, i (i)}
					<li class="plan">
						<header>
							<span class="rank">#{i + 1}</span>
							<span class="metric">composta mitjana <strong>{p.score.toFixed(2)}</strong></span>
							{#if p.totalYears > 0}
								<span class="metric">~{p.totalYears} anys de formació</span>
							{/if}
							{#if p.finalSalary !== undefined}
								<span class="metric">salari modal d'arribada <strong>{eur(p.finalSalary)}</strong></span>
							{/if}
						</header>
						<ol class="plan-flow">
							{#each p.steps as step, idx (step.nodeId)}
								<li class="plan-step">
									<span class="step-pill {categoryClass(step.category)}">{step.label}</span>
									{#if idx > 0 && (step.salary !== undefined || step.pctEmployed !== undefined)}
										<dl class="step-metrics">
											{#if step.salary !== undefined}
												<div><dt>Salari</dt><dd>{eur(step.salary)}</dd></div>
											{/if}
											{#if step.pctEmployed !== undefined}
												<div><dt>Ocupats</dt><dd>{pct(step.pctEmployed)}</dd></div>
											{/if}
											{#if step.pctAdequate !== undefined}
												<div><dt>Adequació</dt><dd>{pct(step.pctAdequate)}</dd></div>
											{/if}
										</dl>
									{/if}
								</li>
							{/each}
						</ol>
					</li>
				{/each}
			</ol>
		{/if}

		<aside class="resources">
			<header>
				<h3>Recursos públics per a aquest camí</h3>
				<p class="hint">
					Filtrats per la teva etapa actual ({stageLabels[selectedStart!.stage]}) i, si escau,
					per la branca de l'objectiu. Cada enllaç ha estat verificat manualment per l'autor.
				</p>
			</header>
			{#each Object.entries(stageResources) as [type, items] (type)}
				{#if items.length > 0}
					<section class="res-group">
						<h4>{groupLabels[type as Resource['type']]}</h4>
						<ul>
							{#each items as r (r.id)}
								<li>
									<a href={r.url} target="_blank" rel="noreferrer">{r.label}</a>
									<span class="res-tag">{r.tag}</span>
									{#if r.blurb}<p class="res-blurb">{r.blurb}</p>{/if}
								</li>
							{/each}
						</ul>
					</section>
				{/if}
			{/each}
			<p class="resources-foot">
				Falten recursos rellevants per a la teva situació? Obre un issue al
				<a href="https://github.com/rebanyat/iara-que/issues" target="_blank" rel="noreferrer">repositori</a>
				i els afegim.
			</p>
		</aside>
	</section>
{:else}
	<section class="container start-empty">
		<p>
			Quan tinguis tots dos punts triats (<strong>1</strong> i <strong>2</strong>), aquí
			apareixerà el planificador amb els camins òptims i els recursos concrets.
		</p>
	</section>
{/if}

<style>
	.intro {
		padding-block: var(--sp-10) var(--sp-4);
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
		font-family: var(--font-serif);
		font-weight: 900;
		line-height: 1.05;
	}

	h1 em {
		color: var(--accent);
		font-style: italic;
		font-weight: 500;
	}

	.lede {
		margin-top: var(--sp-4);
		font-size: 1.0625rem;
		line-height: var(--lh-loose);
		color: var(--ink-secondary);
		max-width: 65ch;
	}

	.wizard {
		display: grid;
		grid-template-columns: 1fr;
		gap: var(--sp-5);
		padding-bottom: var(--sp-6);
		max-width: 1100px;
	}

	@media (min-width: 880px) {
		.wizard {
			grid-template-columns: 1fr 1fr;
		}
	}

	.step-card {
		padding: var(--sp-5);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-lg);
		background: var(--bg-elev);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		min-height: 220px;
		transition: border-color var(--dur-2) var(--ease);
	}

	.step-card.complete {
		border-color: color-mix(in srgb, var(--accent) 40%, var(--border-default));
	}

	.step-card header {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
	}

	.step-num {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 26px;
		height: 26px;
		border-radius: 50%;
		background: var(--bg-base);
		border: 1px solid var(--border-default);
		font-family: var(--font-mono);
		font-size: var(--fs-small);
		color: var(--ink-secondary);
	}

	.step-card.complete .step-num {
		background: var(--accent);
		color: var(--bg-base);
		border-color: var(--accent);
	}

	.step-card h2 {
		font-size: 1.4rem;
		font-family: var(--font-serif);
		font-weight: 700;
	}

	.step-card h2 em {
		font-style: italic;
		color: var(--accent);
	}

	.step-sub {
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		margin-top: calc(var(--sp-2) * -1);
		margin-bottom: var(--sp-2);
		line-height: 1.4;
	}

	.start-box {
		position: relative;
	}

	.start-box input {
		width: 100%;
		padding: var(--sp-2) var(--sp-3);
		font-family: var(--font-sans);
		font-size: 1rem;
		background: var(--bg-base);
		color: var(--ink-primary);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		outline: none;
	}

	.start-box input:focus {
		border-color: var(--accent);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 16%, transparent);
	}

	.start-list {
		position: absolute;
		top: calc(100% + var(--sp-1));
		left: 0;
		right: 0;
		max-height: 280px;
		overflow-y: auto;
		background: var(--bg-surface);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-lg);
		z-index: 20;
		list-style: none;
		padding: var(--sp-1) 0;
		margin: 0;
	}

	.start-list li button {
		width: 100%;
		text-align: left;
		padding: var(--sp-2) var(--sp-3);
		background: transparent;
		border: none;
		display: flex;
		flex-direction: column;
		gap: 2px;
		cursor: pointer;
		color: var(--ink-primary);
	}

	.start-list li button:hover {
		background: color-mix(in srgb, var(--accent) 12%, transparent);
	}

	.start-label {
		font-size: var(--fs-body);
	}

	.start-meta {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}

	.clear-btn {
		position: absolute;
		right: var(--sp-2);
		top: 50%;
		transform: translateY(-50%);
		font-size: 1.25rem;
		color: var(--ink-muted);
		background: transparent;
		border: none;
		padding: 0 var(--sp-1);
		cursor: pointer;
	}

	.clear-btn:hover {
		color: var(--ink-primary);
	}

	.hint {
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		line-height: 1.4;
		font-style: italic;
	}

	.sub-hint {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--ink-muted);
		margin-top: var(--sp-2);
	}

	.esco-wrap {
		margin-bottom: var(--sp-3);
	}

	.goals-scroll {
		max-height: 260px;
		overflow-y: auto;
		padding-right: var(--sp-2);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		padding: var(--sp-2);
		background: color-mix(in srgb, var(--bg-base) 50%, transparent);
	}

	.goals-scroll::-webkit-scrollbar {
		width: 6px;
	}
	.goals-scroll::-webkit-scrollbar-thumb {
		background: var(--border-default);
		border-radius: 3px;
	}

	.goals-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: var(--sp-2);
	}

	.goal-card {
		text-align: left;
		padding: var(--sp-3);
		background: var(--bg-base);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
		cursor: pointer;
		transition: border-color var(--dur-2) var(--ease), background var(--dur-2) var(--ease);
	}

	.goal-card:hover {
		border-color: var(--border-strong);
	}

	.goal-card.active {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 12%, var(--bg-base));
	}

	.goal-label {
		font-weight: 600;
		font-size: var(--fs-small);
		color: var(--ink-primary);
	}

	.goal-blurb {
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		line-height: 1.4;
	}

	.goal-detail {
		margin-top: var(--sp-3);
		padding: var(--sp-3);
		background: color-mix(in srgb, var(--accent) 10%, var(--bg-base));
		border-radius: var(--radius-md);
		border-left: 3px solid var(--accent);
	}

	.goal-detail header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.goal-exempl {
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		margin-top: var(--sp-1);
	}

	.goal-honest {
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		margin-top: var(--sp-2);
		font-style: italic;
		line-height: 1.5;
	}

	.start-empty {
		max-width: 880px;
		padding-block: var(--sp-4) var(--sp-12);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}

	.plans {
		max-width: 1100px;
		padding-bottom: var(--sp-12);
	}

	.plans-head h2 {
		font-size: var(--fs-h2);
		font-family: var(--font-serif);
	}

	.empty {
		color: var(--ink-secondary);
		font-size: var(--fs-small);
		line-height: var(--lh-loose);
		margin-top: var(--sp-3);
		max-width: 60ch;
	}

	.plan-list {
		list-style: none;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		margin: var(--sp-5) 0;
	}

	.plan {
		padding: var(--sp-4) var(--sp-5);
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
	}

	.plan header {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--sp-3);
		font-size: var(--fs-small);
		color: var(--ink-muted);
		margin-bottom: var(--sp-3);
	}

	.rank {
		font-family: var(--font-mono);
		font-weight: 700;
		color: var(--accent);
		font-size: 1.1rem;
	}

	.metric {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}

	.metric strong {
		color: var(--ink-primary);
		font-weight: 600;
	}

	.plan-flow {
		list-style: none;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	.plan-step {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--sp-3);
		position: relative;
		padding-left: var(--sp-4);
	}

	.plan-step::before {
		content: '↓';
		font-family: var(--font-mono);
		color: var(--ink-muted);
		position: absolute;
		top: -8px;
		left: 0;
		font-size: var(--fs-small);
	}

	.plan-step:first-child::before {
		content: '';
	}

	.step-pill {
		padding: var(--sp-1) var(--sp-3);
		border-radius: var(--radius-pill);
		border: 1px solid var(--border-default);
		background: var(--bg-base);
		font-size: var(--fs-small);
		font-weight: 500;
	}

	.step-origin { color: var(--ink-secondary); }
	.step-study { color: var(--accent-cool); border-color: color-mix(in srgb, var(--accent-cool) 30%, var(--border-default)); }
	.step-occupation { color: var(--accent); border-color: color-mix(in srgb, var(--accent) 30%, var(--border-default)); }
	.step-outcome { color: var(--accent-warm); border-color: color-mix(in srgb, var(--accent-warm) 30%, var(--border-default)); }

	.step-metrics {
		display: flex;
		gap: var(--sp-3);
		margin: 0;
	}

	.step-metrics div {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.step-metrics dt {
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--ink-muted);
	}

	.step-metrics dd {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		margin: 0;
	}

	.resources {
		margin-top: var(--sp-6);
		padding: var(--sp-5);
		background: color-mix(in srgb, var(--accent-cool) 8%, var(--bg-elev));
		border: 1px solid color-mix(in srgb, var(--accent-cool) 22%, var(--border-default));
		border-radius: var(--radius-lg);
	}

	.resources header {
		margin-bottom: var(--sp-4);
	}

	.resources h3 {
		font-size: 1.15rem;
		font-weight: 700;
	}

	.resources .hint {
		font-style: normal;
		margin-top: var(--sp-2);
	}

	.res-group {
		margin-top: var(--sp-4);
	}

	.res-group h4 {
		font-size: var(--fs-small);
		font-family: var(--font-mono);
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--accent-cool);
		margin-bottom: var(--sp-2);
	}

	.res-group ul {
		list-style: none;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	.res-group li {
		padding: var(--sp-2) var(--sp-3);
		border-left: 2px solid color-mix(in srgb, var(--accent-cool) 35%, transparent);
		background: var(--bg-base);
		border-radius: var(--radius-sm);
	}

	.res-group a {
		color: var(--ink-primary);
		font-weight: 600;
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.res-group a:hover {
		color: var(--accent-cool);
	}

	.res-tag {
		display: inline-block;
		margin-left: var(--sp-2);
		font-family: var(--font-mono);
		font-size: 9px;
		letter-spacing: 0.05em;
		padding: 1px 4px;
		border: 1px solid var(--border-default);
		border-radius: var(--radius-sm);
		color: var(--ink-muted);
	}

	.res-blurb {
		margin-top: var(--sp-1);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		line-height: 1.4;
	}

	.resources-foot {
		margin-top: var(--sp-5);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		font-style: italic;
	}

	.resources-foot a {
		color: var(--accent-cool);
	}
</style>
