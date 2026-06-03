<script lang="ts">
	import Sankey from '$lib/viz/Sankey.svelte';
	import SankeyTable from '$lib/viz/SankeyTable.svelte';
	import FilterChips from '$lib/ui/FilterChips.svelte';
	import Legend from '$lib/ui/Legend.svelte';
	import SearchBox from '$lib/ui/SearchBox.svelte';
	import SidePanel from '$lib/ui/SidePanel.svelte';
	import { page } from '$app/state';

	const view = $derived(page.url.searchParams.get('view') === 'table' ? 'table' : 'chart');
	const otherView = $derived(view === 'table' ? '' : 'table');
	const toggleHref = $derived.by(() => {
		const sp = new URLSearchParams(page.url.searchParams);
		if (otherView) sp.set('view', otherView);
		else sp.delete('view');
		const s = sp.toString();
		return s ? `/?${s}` : '/';
	});
</script>

<svelte:head>
	<title>I ara, què? — Atles d'itineraris reals</title>
</svelte:head>

<section class="hero container">
	<p class="eyebrow">Atles d'itineraris reals · Catalunya · 2014–2023</p>
	<h1 class="display">
		<span class="display-line">Tries un camí formatiu.</span>
		<span class="display-line"><em>Què acaba passant?</em></span>
	</h1>
	<p class="lede">
		Quan algú surt de l'ESO i tria FP, batxillerat o universitat, deixa un rastre estadístic
		documentat per AQU, MEFP, Idescat i l'Observatori del Treball. Aquest atles reconstrueix
		els camins agregats <strong>de la formació a la feina</strong>, amb empleabilitat, salari,
		adequació i bretxes per gènere i territori.
	</p>
</section>

<section class="viz container">
	<SearchBox />
	<FilterChips />

	<div class="view-toggle">
		<a href={toggleHref} data-sveltekit-keepfocus data-sveltekit-noscroll class="view-link">
			{view === 'table' ? '← Tornar al sankey' : 'Vista en taula (accessible) →'}
		</a>
	</div>

	{#if view === 'table'}
		<SankeyTable />
	{:else}
		<Sankey />
		<Legend />
		<SidePanel />
	{/if}

	<p class="caption">
		Volums alimentats per <strong>Idescat</strong> i <strong>MEFP</strong>; salari,
		empleabilitat i adequació, per <strong>AQU</strong> (informes 2023) i
		<strong>Consell de Cambres</strong> (2022). Passa el cursor per qualsevol aresta per
		veure'n la mètrica i la font; fes clic per fixar-la. La intensitat del color codifica
		la mètrica seleccionada més amunt; el gruix, el volum agregat. Existeix una vista en
		<a href="/?view=table">taula HTML</a> per a lectors de pantalla.
	</p>
</section>

<style>
	.hero {
		padding-block: var(--sp-10) var(--sp-6);
		max-width: 1200px;
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--ink-muted);
		margin-bottom: var(--sp-5);
	}

	.display {
		font-size: var(--fs-display);
		line-height: 1.05;
		font-weight: 900;
		max-width: 18ch;
	}

	.display-line {
		display: block;
	}

	.display em {
		font-style: italic;
		color: var(--accent);
		font-weight: 500;
	}

	.lede {
		margin-top: var(--sp-6);
		max-width: 60ch;
		font-size: 1.125rem;
		line-height: var(--lh-loose);
		color: var(--ink-secondary);
	}

	.lede strong {
		color: var(--ink-primary);
		font-weight: 600;
	}

	.viz {
		padding-bottom: var(--sp-10);
	}

	.view-toggle {
		display: flex;
		justify-content: flex-end;
		margin-bottom: var(--sp-3);
	}

	.view-link {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-secondary);
		padding: var(--sp-1) var(--sp-3);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-pill);
		border-bottom: 1px solid var(--border-default);
		transition: color var(--dur-2) var(--ease), border-color var(--dur-2) var(--ease);
	}

	.view-link:hover,
	.view-link:focus-visible {
		color: var(--ink-primary);
		border-color: var(--border-strong);
	}

	.caption {
		margin-top: var(--sp-3);
		max-width: 80ch;
		color: var(--ink-muted);
		font-size: var(--fs-small);
		line-height: var(--lh-loose);
	}

	.caption strong {
		color: var(--ink-secondary);
		font-weight: 600;
	}
</style>
