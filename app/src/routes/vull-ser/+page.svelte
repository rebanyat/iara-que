<svelte:head>
	<title>Vull ser… — I ara, què?</title>
</svelte:head>

<section class="container stub">
	<p class="eyebrow">Q6 · explorador d'objectius</p>
	<h1>Vull ser…</h1>
	<p class="lede">
		Escriu o tria una professió i veuràs els camins documentats que hi porten — des de
		titulacions universitàries i cicles d'FP fins a perfils icònics de Wikidata
		(astronautes, premis Nobel, persones que regenten una empresa pròpia, etc.).
	</p>
	<p class="hint">Funcionalitat en desenvolupament.</p>
</section>

<style>
	.stub {
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

	.lede {
		margin-top: var(--sp-5);
		font-size: 1.125rem;
		line-height: var(--lh-loose);
		color: var(--ink-secondary);
	}

	.hint {
		margin-top: var(--sp-8);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}
</style>
