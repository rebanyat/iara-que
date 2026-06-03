<script lang="ts">
	import { activeSelection } from '$lib/stores/activeSelection';

	// Hardcoded reference values, each cited on the methodology page.
	// Sources are short-form here so the side-panel card stays compact.
	const REFS = {
		// Observatori Català de la Joventut "Sistema d'Indicadors sobre la
		// Joventut a Catalunya" (2024 edition, dades 2023): mediana de
		// l'esforç econòmic d'accés a l'habitatge per a joves 16–29 anys
		// és del 64,7 % del salari (compra) i del 92,9 % (lloguer).
		// Ratio cost-mig habitatge / salari brut anual mig jove ≈ 11,2 anys.
		yearsToFlat: 11.2,
		yearsToFlat2010: 6.4,
		// INE IPC general 2008-12 = 100 → ~140 a 2025. Sou nominal mediana
		// jove Catalunya 2008 ~ 18.700 €; 2024 ~ 20.300 €. Poder adquisitiu
		// real cau ≈ 24 %.
		purchasingPowerLossPct: 0.24,
		// Observatori d'Emancipació CJE 2024 — proporció joves 16-29 que
		// poden emancipar-se amb el seu salari: 17,6 %.
		emancipationRate: 0.176
	};

	const sel = $derived($activeSelection);

	function pct(x: number): string {
		return new Intl.NumberFormat('ca-ES', { style: 'percent', maximumFractionDigits: 0 }).format(x);
	}

	function years(x: number): string {
		const n = new Intl.NumberFormat('ca-ES', { maximumFractionDigits: 1 }).format(x);
		return `${n} anys`;
	}

	const targetLabel = $derived.by(() => {
		if (sel.searchTarget) return sel.searchTarget.label;
		if (sel.branca.length > 0) return `el camí ${sel.branca[0].replace('branca__', '')}`;
		return 'qualsevol camí mitjà';
	});
</script>

<div class="reality">
	<header>
		<h3>Reality check</h3>
		<p class="sub">
			El sankey mostra resultats laborals. Aquesta caixa els relativitza —
			perquè un salari raonable a 2024 no compra el mateix que el 2010, ni la
			feina pesa igual sense un sostre on aterrar.
		</p>
	</header>

	<ul class="metrics">
		<li>
			<span class="num accent">{years(REFS.yearsToFlat)}</span>
			<span class="label">de sou íntegre per pagar un pis mitjà <span class="ctx">a Catalunya, 2024</span></span>
			<span class="contrast">vs {years(REFS.yearsToFlat2010)} el 2010</span>
		</li>
		<li>
			<span class="num warm">−{pct(REFS.purchasingPowerLossPct)}</span>
			<span class="label">de poder adquisitiu real <span class="ctx">joves 16–29 vs 2008</span></span>
			<span class="contrast">salari nominal puja ~9 %, IPC puja ~40 %</span>
		</li>
		<li>
			<span class="num cool">{pct(REFS.emancipationRate)}</span>
			<span class="label">de joves es poden emancipar amb el seu sou <span class="ctx">2024</span></span>
			<span class="contrast">era el 41 % el 2008 (CJE)</span>
		</li>
	</ul>

	<aside class="hope">
		<p class="hope-title">Què pots fer ara amb el camí de {targetLabel}</p>
		<ul>
			<li>
				<a href="https://orienta.gencat.cat" target="_blank" rel="noreferrer">Orientació pública gratuïta del SOC</a>
				· cita amb un orientador laboral en menys de 15 dies.
			</li>
			<li>
				<a href="https://agaur.gencat.cat" target="_blank" rel="noreferrer">Beques AGAUR + MEFP</a>
				· cobreixen matrícula i una part del manteniment per a rendes baixes/mitjanes.
			</li>
			<li>
				<a href="https://www.ccoo.cat/joves" target="_blank" rel="noreferrer">Avantatges juvenils sindicals</a>
				· assessoria gratuïta per al primer contracte i drets laborals.
			</li>
			<li>
				<a href="https://habitatge.gencat.cat" target="_blank" rel="noreferrer">Bo lloguer jove + borsa de mediació</a>
				· no resol el sostre del mercat, però alleugereix els primers 250–450 €/mes.
			</li>
		</ul>
	</aside>
</div>

<style>
	.reality {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	header h3 {
		font-size: 1.05rem;
		font-weight: 700;
	}

	header h3::before {
		content: '03 · ';
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
		max-width: 55ch;
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
</style>
