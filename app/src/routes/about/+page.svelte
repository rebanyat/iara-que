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
		de Catalunya en una mateixa vista — d'ESO a la primera feina, passant per FP, batxillerat,
		grau, màster i la composició salari/adequació/territori que es deriva de cada camí.
	</p>

	<h2>Llicència</h2>
	<ul>
		<li><strong>Codi font</strong> — MIT.</li>
		<li><strong>Continguts, visualitzacions, microcopy</strong> — CC BY 4.0.</li>
		<li><strong>Dades</strong> — cada font conserva la seva llicència; detall a <a href="/metodologia">Metodologia</a>.</li>
	</ul>

	<h2>Repositori</h2>
	<p>
		Codi públic a
		<a href="https://github.com/rebanyat/iara-que" rel="noopener">github.com/rebanyat/iara-que</a>
		— SvelteKit + D3 + Vercel.
	</p>

	<h2>Ús d'IA</h2>
	<p>
		El procés ha incorporat assistència de l'IA assistent <em>Anthropic Claude</em> per a la
		implementació de codi i esborrany de text, sota la política d'IA de la UOC. Cada decisió
		de disseny, valor numèric i decisió de scope s'ha pres i revisat per l'autor. Detall i
		registre a <a href="/metodologia#ia">Metodologia · IA</a>.
	</p>

	<h2>Stack i agraïments</h2>
	<ul>
		<li><a href="https://kit.svelte.dev" rel="noopener">SvelteKit</a> + <a href="https://d3js.org" rel="noopener">D3.js</a> + <a href="https://vercel.com" rel="noopener">Vercel</a>.</li>
		<li><a href="https://github.com/topojson/topojson-client" rel="noopener">topojson-client</a> + <a href="https://github.com/nextapps-de/flexsearch" rel="noopener">FlexSearch</a>.</li>
		<li>Tipografia: <em>Fraunces</em> (titulars), <em>Inter</em> (UI), <em>JetBrains Mono</em> (dades).</li>
		<li>
			Topojson de comarques: derivat del repositori obert
			<a href="https://github.com/sirisacademic/catalonia-cartography" rel="noopener">sirisacademic/catalonia-cartography</a>.
		</li>
	</ul>
</section>

<style>
	.doc {
		padding-block: var(--sp-10) var(--sp-12);
		max-width: 760px;
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

	p strong {
		color: var(--ink-primary);
	}
</style>
