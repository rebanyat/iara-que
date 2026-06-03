<script lang="ts">
	import TopOccupations from '$lib/viz/TopOccupations.svelte';
	import GenderDumbbell from '$lib/viz/GenderDumbbell.svelte';
	import { activeSelection } from '$lib/stores/activeSelection';
	import { clearSearchTarget } from '$lib/stores/selection';
	import { resetFilters } from '$lib/stores/filters';

	function clearAll() {
		clearSearchTarget();
		resetFilters();
	}

	const sel = $derived($activeSelection);

	const modeLabel = $derived(
		sel.mode === 'initial'
			? 'Vista general'
			: sel.mode === 'filtered'
				? 'Filtrat'
				: sel.mode === 'targeted'
					? 'Objectiu actiu'
					: 'Aresta fixada'
	);
</script>

<aside class="side-panel" aria-label="Panells contextuals">
	<header class="state">
		<div class="state-info">
			<span class="state-tag">{modeLabel}</span>
			{#if sel.searchTarget}
				<span class="state-line">→ {sel.searchTarget.label}</span>
			{:else if sel.branca.length > 0}
				<span class="state-line">→ {sel.branca.length} branca{sel.branca.length > 1 ? 's' : ''} actives</span>
			{:else}
				<span class="state-line muted">tot l'atles a la vista</span>
			{/if}
		</div>
		{#if sel.mode !== 'initial'}
			<button type="button" class="state-clear" onclick={clearAll} aria-label="Restablir vista">
				Vista general
			</button>
		{/if}
	</header>

	<div class="grid">
		<section class="card">
			<TopOccupations />
		</section>

		<section class="card">
			<GenderDumbbell />
		</section>

		<section class="card card-skeleton">
			<h3>Mapa comarcal</h3>
			<p class="skeleton-hint">Mapa coroplètic de Catalunya per comarca — arriba properament amb l'Observatori del Treball.</p>
			<div class="skeleton-map" aria-hidden="true"></div>
		</section>

		<section class="card card-skeleton">
			<h3>Evolució 2014 → 2023</h3>
			<p class="skeleton-hint">Sèries temporals d'empleabilitat composta per branca — arriba properament.</p>
			<div class="skeleton-lines" aria-hidden="true">
				<svg viewBox="0 0 200 80" preserveAspectRatio="none">
					<polyline points="0,60 50,52 100,40 150,30 200,20" fill="none" stroke="currentColor" stroke-width="2"></polyline>
					<polyline points="0,68 50,64 100,58 150,52 200,46" fill="none" stroke="currentColor" stroke-width="2" opacity="0.55"></polyline>
					<polyline points="0,74 50,71 100,68 150,66 200,64" fill="none" stroke="currentColor" stroke-width="2" opacity="0.30"></polyline>
				</svg>
			</div>
		</section>
	</div>
</aside>

<style>
	.side-panel {
		margin-top: var(--sp-6);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.state {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-3);
		padding: var(--sp-3) var(--sp-4);
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		flex-wrap: wrap;
	}

	.state-info {
		display: flex;
		align-items: baseline;
		gap: var(--sp-3);
		min-width: 0;
	}

	.state-tag {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--accent);
		flex-shrink: 0;
	}

	.state-line {
		font-size: var(--fs-small);
		color: var(--ink-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.state-line.muted {
		color: var(--ink-muted);
		font-style: italic;
	}

	.state-clear {
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		color: var(--ink-muted);
		padding: var(--sp-1) var(--sp-3);
		border-radius: var(--radius-md);
		border: 1px solid var(--border-default);
		transition: color var(--dur-2) var(--ease);
	}

	.state-clear:hover {
		color: var(--ink-primary);
		border-color: var(--border-strong);
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: var(--sp-4);
	}

	@media (max-width: 880px) {
		.grid {
			grid-template-columns: 1fr;
		}
	}

	.card {
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: var(--sp-5);
	}

	.card-skeleton {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
		color: var(--ink-secondary);
	}

	.card-skeleton h3 {
		font-size: 1.05rem;
		font-weight: 700;
	}

	.skeleton-hint {
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}

	.skeleton-map {
		flex: 1;
		min-height: 160px;
		border-radius: var(--radius-md);
		background:
			radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--accent) 12%, transparent), transparent 55%),
			radial-gradient(circle at 70% 60%, color-mix(in srgb, var(--accent-cool) 12%, transparent), transparent 55%),
			color-mix(in srgb, var(--bg-surface) 92%, transparent);
		border: 1px dashed var(--border-default);
	}

	.skeleton-lines {
		flex: 1;
		min-height: 120px;
		color: color-mix(in srgb, var(--accent) 60%, transparent);
	}

	.skeleton-lines svg {
		width: 100%;
		height: 100%;
		display: block;
	}
</style>
