<svelte:head>
	<title>Metodologia — I ara, què?</title>
</svelte:head>

<section class="container doc">
	<p class="eyebrow">com s'ha fet</p>
	<h1>Metodologia</h1>

	<h2>Fonts de dades</h2>
	<ul>
		<li><strong>AQU Catalunya</strong> — Enquesta d'inserció laboral universitària (onades 2014, 2017, 2020, 2023). Informes públics agregats; les microdades estan sol·licitades formalment però no s'han rebut en finestra.</li>
		<li><strong>Consell de Cambres + Departament d'Educació</strong> — Estudi d'inserció laboral dels ensenyaments professionals.</li>
		<li><strong>Idescat</strong> — Estadística de l'ensenyament (universitari i no universitari), taula <code>ilgu</code> d'inserció laboral de graduats.</li>
		<li><strong>MEFP</strong> — Estadística estatal d'FP.</li>
		<li><strong>Observatori del Treball i Model Productiu</strong> — Consultes interactives de contractació, atur i salaris per comarca.</li>
		<li><strong>SEPE</strong> — Estadística de contractes i ocupació registrada.</li>
		<li><strong>ESCO v1.2.1</strong> — Taxonomia europea d'ocupacions i competències; clau mestra d'enriquiment.</li>
		<li><strong>Wikidata SPARQL</strong> — Camins educatius de figures icòniques (capa aspiracional).</li>
		<li><strong>OECD Education at a Glance</strong> — Benchmark internacional.</li>
	</ul>

	<h2>Limitacions i biaixos</h2>
	<p>Es descriuran aquí: biaix de no-resposta a les enquestes d'inserció, biaix temporal (mesura a 3 anys), biaix de desagregació (cel·les petites suprimides per anonimat), absència d'itineraris informals (autoformació, formació d'empresa) i biaix territorial (algunes variables només existeixen a nivell provincial).</p>

	<h2>Ús d'intel·ligència artificial</h2>
	<p>Conforme a la política d'IA de la UOC, qualsevol ús d'eines d'IA en l'elaboració del projecte queda documentat aquí i a <code>docs/ai_usage.md</code> del repositori.</p>

	<p class="hint">Document en desenvolupament.</p>
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
		gap: var(--sp-3);
	}

	ul strong {
		color: var(--ink-primary);
	}

	p {
		margin-top: var(--sp-3);
		color: var(--ink-secondary);
		line-height: var(--lh-loose);
	}

	.hint {
		margin-top: var(--sp-8);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}

	code {
		background: var(--bg-elev);
		padding: 0 var(--sp-1);
		border-radius: var(--radius-sm);
		font-size: 0.95em;
	}
</style>
