<script lang="ts">
	import Sankey from '$lib/viz/Sankey.svelte';
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
	<Sankey />
	<p class="caption">
		Versió inicial — proporcions parcialment estimades fins a la integració completa de les
		fonts AQU. Les arestes marcades com a <em>placeholder</em> es substituiran a mesura que es
		processin els informes públics.
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

	.caption {
		margin-top: var(--sp-3);
		max-width: 80ch;
		color: var(--ink-muted);
		font-size: var(--fs-small);
		line-height: var(--lh-loose);
	}

	.caption em {
		font-style: italic;
		color: var(--ink-secondary);
	}
</style>
