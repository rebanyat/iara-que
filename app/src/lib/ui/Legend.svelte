<script lang="ts">
	import { filters, setColorMetric, type ColorMetric } from '$lib/stores/filters';

	const METRICS: { id: ColorMetric; label: string; desc: string }[] = [
		{ id: 'composite', label: 'empleabilitat composta', desc: 'combinació ponderada d\'ocupació, adequació, salari i indefinit' },
		{ id: 'salary', label: 'salari modal', desc: 'salari brut anual mitjà' },
		{ id: 'employed', label: '% ocupats', desc: 'taxa d\'ocupació a 3 anys' },
		{ id: 'adequate', label: '% adequació', desc: '% feina d\'alta adequació al títol' }
	];

	const CATEGORY_COLOR = {
		origin: '#7B8395',
		study: '#4FB6D0',
		occupation: '#FFC857',
		outcome: '#E0533D'
	};
</script>

<div class="legend">
	<div class="categories" aria-hidden="true">
		<span class="dot" style="background: {CATEGORY_COLOR.origin}"></span> origen
		<span class="dot" style="background: {CATEGORY_COLOR.study}"></span> formació
		<span class="dot" style="background: {CATEGORY_COLOR.occupation}"></span> ocupació
		<span class="dot" style="background: {CATEGORY_COLOR.outcome}"></span> outcome
	</div>

	<fieldset class="metric-switch">
		<legend>color de l'aresta</legend>
		<div class="metric-row" role="radiogroup">
			{#each METRICS as m (m.id)}
				<button
					type="button"
					class="m-btn"
					class:active={$filters.colorMetric === m.id}
					role="radio"
					aria-checked={$filters.colorMetric === m.id}
					title={m.desc}
					onclick={() => setColorMetric(m.id)}
				>
					{m.label}
				</button>
			{/each}
		</div>
		<div class="scale" aria-hidden="true">
			<span class="scale-min">baix</span>
			<span class="scale-track"></span>
			<span class="scale-max">alt</span>
		</div>
	</fieldset>
</div>

<style>
	.legend {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		margin-top: var(--sp-4);
		padding: var(--sp-3) var(--sp-4);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		background: var(--bg-elev);
	}

	.categories {
		display: flex;
		flex-wrap: wrap;
		gap: var(--sp-4);
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
	}

	.dot {
		display: inline-block;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		margin-right: 6px;
		vertical-align: -1px;
	}

	.metric-switch {
		border: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: auto auto;
		column-gap: var(--sp-4);
		row-gap: var(--sp-2);
		align-items: center;
	}

	.metric-switch legend {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--ink-muted);
		padding: 0;
		grid-column: 1 / -1;
	}

	.metric-row {
		display: flex;
		gap: var(--sp-1);
		flex-wrap: wrap;
		grid-column: 1 / 2;
	}

	.m-btn {
		padding: var(--sp-1) var(--sp-3);
		font-family: var(--font-sans);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-pill);
		transition:
			background var(--dur-2) var(--ease),
			color var(--dur-2) var(--ease),
			border-color var(--dur-2) var(--ease);
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

	.scale {
		grid-column: 2 / 3;
		display: grid;
		grid-template-columns: auto 1fr auto;
		column-gap: var(--sp-2);
		align-items: center;
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		min-width: 220px;
	}

	.scale-track {
		height: 8px;
		border-radius: var(--radius-pill);
		background: linear-gradient(
			90deg,
			#3b1f2b 0%,
			#b53a4c 35%,
			#e07c42 60%,
			#f2c25d 100%
		);
	}

	@media (max-width: 640px) {
		.metric-switch {
			grid-template-columns: 1fr;
		}
		.metric-row,
		.scale {
			grid-column: 1 / -1;
		}
	}
</style>
