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

	<div class="placeholder" role="img" aria-label="La visualització principal apareixerà aquí (en construcció).">
		<div class="placeholder-rule"></div>
		<div class="placeholder-rule placeholder-rule--mid"></div>
		<div class="placeholder-rule placeholder-rule--short"></div>
		<p class="placeholder-label">
			<span class="mono">[ sankey hero · en construcció ]</span>
		</p>
	</div>

	<p class="hint">
		Versió inicial — els filtres, la visualització interactiva i la cerca
		<em>"vull ser…"</em> s'aniran incorporant durant les properes iteracions.
	</p>
</section>

<style>
	.hero {
		padding-block: var(--sp-10) var(--sp-8);
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

	.placeholder {
		margin-top: var(--sp-10);
		padding: var(--sp-8);
		border: 1px dashed var(--border-default);
		border-radius: var(--radius-lg);
		background: var(--bg-elev);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
		align-items: stretch;
		min-height: 420px;
		justify-content: center;
	}

	.placeholder-rule {
		height: 12px;
		border-radius: var(--radius-pill);
		background: linear-gradient(90deg, var(--edge-2), var(--edge-3), var(--edge-4));
		opacity: 0.45;
		width: 100%;
	}

	.placeholder-rule--mid { width: 78%; opacity: 0.32; }
	.placeholder-rule--short { width: 52%; opacity: 0.22; }

	.placeholder-label {
		text-align: center;
		color: var(--ink-muted);
		font-size: var(--fs-small);
		margin-top: var(--sp-4);
	}

	.hint {
		margin-top: var(--sp-5);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}
</style>
