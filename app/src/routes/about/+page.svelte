<svelte:head>
	<title>Crèdits — I ara, què?</title>
</svelte:head>

<section class="container doc">
	<p class="eyebrow">qui · com · llicència</p>
	<h1>Crèdits</h1>

	<h2>Autoria</h2>
	<p>
		<strong>Ivan Rodríguez Quintana</strong> — estudiant del grau de Ciència de Dades Aplicada
		de la Universitat Oberta de Catalunya. Projecte final de l'assignatura
		<em>Visualització de Dades</em>, semestre 2026.
	</p>

	<h2>Per què</h2>
	<p>
		La meva mare és orientadora professional. Aquest projecte neix per dotar-la d'una eina
		operativa amb dades reals que cobreixi tots els itineraris formatius i laborals públics
		de Catalunya en una mateixa vista.
	</p>

	<h2>Llicència</h2>
	<ul>
		<li><strong>Codi font</strong> — MIT.</li>
		<li><strong>Continguts i visualitzacions</strong> — CC BY 4.0.</li>
		<li><strong>Dades</strong> — cada font conserva la seva llicència; veure <a href="/metodologia">Metodologia</a>.</li>
	</ul>

	<h2>Repositori</h2>
	<p>
		El codi està disponible públicament a
		<a href="https://github.com/rebanyat/iara-que">github.com/rebanyat/iara-que</a>.
	</p>
</section>

<style>
	.doc {
		padding-block: var(--sp-10) var(--sp-12);
		max-width: 720px;
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--ink-muted);
		margin-bottom: var(--sp-4);
	}

	h1 {
		font-size: var(--fs-h1);
	}

	h2 {
		font-size: var(--fs-h2);
		margin-top: var(--sp-8);
		margin-bottom: var(--sp-4);
	}

	ul {
		margin: 0;
		padding-left: var(--sp-5);
		color: var(--ink-secondary);
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	ul strong {
		color: var(--ink-primary);
	}

	p {
		margin-top: var(--sp-3);
		color: var(--ink-secondary);
		line-height: var(--lh-loose);
	}

	p strong { color: var(--ink-primary); }

	.hint {
		margin-top: var(--sp-8);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}
</style>
