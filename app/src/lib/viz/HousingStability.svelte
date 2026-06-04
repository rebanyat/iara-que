<script lang="ts">
	// Sources:
	// - Observatori d'Emancipació CJE 2024: edat mitjana d'emancipació
	//   30,3 anys (Catalunya). 17,6 % de joves 16-29 emancipats.
	//   Esforç de compra mediana: 64,7 % del salari. Esforç lloguer
	//   mediana: 92,9 % del salari (joves).
	// - INE EPA: 41 % de joves 25-29 vivien sols el 2008. 2024: 18 %.
	// - Sindicat de Llogateres / Llogateres de Barcelona: 2024 informe.

	function pct(x: number): string {
		return new Intl.NumberFormat('ca-ES', { style: 'percent', maximumFractionDigits: 0 }).format(x);
	}

	function age(x: number): string {
		const n = new Intl.NumberFormat('ca-ES', { maximumFractionDigits: 1 }).format(x);
		return `${n} anys`;
	}
</script>

<div class="critique">
	<header>
		<h3>Sense sostre, no hi ha estabilitat</h3>
		<p class="sub">
			La feina ja no és la palanca per a construir una vida; l'<em>habitatge</em>
			ho és. I l'habitatge ha tornat a ser inaccessible. No poder-se emancipar a
			temps no és un fracàs individual: és una decisió política que es pot revertir.
		</p>
	</header>

	<ul class="metrics">
		<li>
			<span class="num accent">{age(30.3)}</span>
			<span class="label">edat mitjana d'emancipació a Catalunya <span class="ctx">2024</span></span>
			<span class="contrast">era de 26,8 anys el 2008</span>
		</li>
		<li>
			<span class="num warm">{pct(0.929)}</span>
			<span class="label">del salari mitjà jove per pagar un lloguer <span class="ctx">CJE 2024</span></span>
			<span class="contrast">la recomanació de l'INE és ≤ 30 %</span>
		</li>
		<li>
			<span class="num cool">{pct(0.18)}</span>
			<span class="label">joves de 25 a 29 anys que viuen sols <span class="ctx">enfront del {pct(0.41)} el 2008</span></span>
			<span class="contrast">la dependència familiar prolongada s'ha tornat estructural</span>
		</li>
	</ul>

	<aside class="hope">
		<p class="hope-title">Què pots fer per recuperar el dret a un sostre</p>
		<ul>
			<li>
				<a href="https://sindicatdellogateres.org" target="_blank" rel="noreferrer">Sindicat de Llogateres</a>
				· acompanyament gratuït per a defensar-te d'augments abusius i d'assetjament
				immobiliari. La llei 12/2023 limita les pujades, però hi ha qui la incompleix.
			</li>
			<li>
				<a href="https://habitatge.gencat.cat" target="_blank" rel="noreferrer">Bo lloguer jove de 250 €/mes</a>
				· no resol el preu, però alleugereix dos anys als joves menors de 35.
			</li>
			<li>
				<a href="https://habitatge.gencat.cat" target="_blank" rel="noreferrer">Servei d'intermediació davant d'un desnonament</a>
				· si reps una demanda d'execució, no signis res sense parlar-ne abans aquí.
			</li>
			<li>
				<a href="https://habitatge.barcelona/ca" target="_blank" rel="noreferrer">Borses d'habitatge públic i assequible</a>
				· apuntar-s'hi aviat és gratuït i no et compromet a res.
			</li>
		</ul>
		<p class="rally">
			Tenir feina sense tenir casa és l'única estabilitat que t'ofereix el mercat.
			L'estabilitat real es conquereix col·lectivament.
		</p>
	</aside>
</div>

<style>
	.critique {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	header h3 {
		font-size: 1.05rem;
		font-weight: 700;
	}

	header h3::before {
		content: '02 · ';
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.08em;
		color: var(--ink-muted);
		font-weight: 500;
	}

	.sub {
		margin-top: var(--sp-1);
		color: var(--ink-secondary);
		font-size: var(--fs-small);
		line-height: 1.5;
		max-width: 60ch;
	}

	.sub em {
		color: var(--accent-cool);
		font-style: italic;
	}

	.metrics {
		display: grid;
		grid-template-columns: 1fr;
		gap: var(--sp-3);
	}

	.metrics li {
		display: grid;
		grid-template-columns: minmax(110px, max-content) 1fr;
		grid-template-rows: auto auto;
		grid-column-gap: var(--sp-3);
		grid-row-gap: 2px;
		align-items: baseline;
		padding: var(--sp-2) var(--sp-3);
		border-left: 3px solid var(--border-default);
		background: color-mix(in srgb, var(--bg-base) 50%, transparent);
	}

	.num {
		grid-row: 1 / span 2;
		font-family: var(--font-mono);
		font-feature-settings: 'tnum' 1;
		font-size: 1.5rem;
		font-weight: 700;
		line-height: 1;
	}

	.num.accent { color: var(--accent); }
	.num.warm { color: var(--accent-warm); }
	.num.cool { color: var(--accent-cool); }

	.label {
		font-size: var(--fs-small);
		color: var(--ink-primary);
		line-height: 1.3;
	}

	.ctx {
		color: var(--ink-muted);
		font-style: italic;
		font-size: var(--fs-micro);
	}

	.contrast {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}

	.hope {
		margin-top: var(--sp-2);
		padding: var(--sp-3) var(--sp-4);
		background: color-mix(in srgb, var(--accent-cool) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--accent-cool) 25%, var(--border-default));
		border-radius: var(--radius-md);
	}

	.hope-title {
		font-weight: 600;
		font-size: var(--fs-small);
		margin-bottom: var(--sp-2);
		color: var(--accent-cool);
	}

	.hope ul {
		list-style: disc;
		padding-left: var(--sp-5);
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	.hope li {
		font-size: var(--fs-small);
		line-height: 1.4;
		color: var(--ink-secondary);
	}

	.hope a {
		color: var(--accent-cool);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.rally {
		margin-top: var(--sp-3);
		padding-top: var(--sp-3);
		border-top: 1px dashed color-mix(in srgb, var(--accent-cool) 35%, var(--border-default));
		font-size: var(--fs-small);
		font-style: italic;
		color: var(--ink-primary);
		line-height: 1.5;
	}
</style>
