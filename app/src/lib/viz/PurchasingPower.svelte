<script lang="ts">
	// Sources:
	// - CCOO "Informe mercat de treball Catalunya 2024" — salari mediana
	//   nominal: ~26.000€ (2023); salari mediana real (€ constants 2014):
	//   ~21.300€ — caiguda real ≈ 7 % en una dècada.
	// - Convenis Generalitat (2024): ~58 % de la població ocupada amb
	//   conveni col·lectiu vigent caducat o sense actualitzar.
	// - Sindicació: Espanya 13,6 % afiliació sindical (UE-27 mitjana 22 %).
	//   Catalunya: 14,3 % (CCOO + UGT + altres). Font: OCDE Trade Union 2023.
	// - INE EPA 2024 T1: 28 % d'assalariats joves (16-29) en temporal.

	function pct(x: number): string {
		return new Intl.NumberFormat('ca-ES', { style: 'percent', maximumFractionDigits: 0 }).format(x);
	}
</script>

<div class="critique">
	<header>
		<h3>Salari nominal puja, salari real cau</h3>
		<p class="sub">
			Els <em>números</em> dels informes laborals miren bé en €. Però el que el sou
			compra cada any és menys, perquè l'IPC corre més de pressa que els convenis.
			Per això la sindicació importa: sense pressió col·lectiva no hi ha actualitzacions.
		</p>
	</header>

	<ul class="metrics">
		<li>
			<span class="num accent">−7 %</span>
			<span class="label">salari real mediana Catalunya <span class="ctx">2014 → 2023, € constants</span></span>
			<span class="contrast">malgrat que en nominal va pujar +18 %</span>
		</li>
		<li>
			<span class="num warm">{pct(0.143)}</span>
			<span class="label">afiliació sindical a Catalunya <span class="ctx">vs {pct(0.22)} mitjana UE-27</span></span>
			<span class="contrast">on menys sindicació, menys actualització salarial</span>
		</li>
		<li>
			<span class="num cool">{pct(0.28)}</span>
			<span class="label">joves assalariats en temporal <span class="ctx">16–29 anys, EPA 2024 T1</span></span>
			<span class="contrast">la temporalitat erosiona la capacitat de negociar</span>
		</li>
	</ul>

	<aside class="hope">
		<p class="hope-title">Què pots fer per pressionar el sou real</p>
		<ul>
			<li>
				<a href="https://www.ccoo.cat/joves" target="_blank" rel="noreferrer">Afilia't a un sindicat jove</a>
				· quota reduïda primer any, assessoria laboral gratuïta, i pes a la mesa de negociació del teu sector.
			</li>
			<li>
				<a href="https://web.gencat.cat/ca/tramits/tramits-temes/Convenis-collectius" target="_blank" rel="noreferrer">Consulta el conveni del teu sector</a>
				· molts són caducats i obligar-ne la renovació toca al treballador, no a l'empresa.
			</li>
			<li>
				<a href="https://www.epa.ine.es" target="_blank" rel="noreferrer">Compara el teu sou real amb l'EPA</a>
				· veure si pagues "preu jove" et dona arguments concrets per renegociar.
			</li>
		</ul>
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
		content: '01 · ';
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
		color: var(--accent);
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
		background: color-mix(in srgb, var(--accent) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--accent) 25%, var(--border-default));
		border-radius: var(--radius-md);
	}

	.hope-title {
		font-weight: 600;
		font-size: var(--fs-small);
		margin-bottom: var(--sp-2);
		color: var(--accent);
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
		color: var(--accent);
		text-decoration: underline;
		text-underline-offset: 2px;
	}
</style>
