<script lang="ts">
	import { activeSelection } from '$lib/stores/activeSelection';

	const sel = $derived($activeSelection);

	const targetLabel = $derived.by(() => {
		if (sel.searchTarget) return sel.searchTarget.label;
		if (sel.branca.length > 0) return `la branca ${sel.branca[0].replace('branca__', '')}`;
		return 'qualsevol itinerari';
	});
</script>

<div class="reality">
	<header>
		<h3>Síntesi · l'estabilitat es conquereix</h3>
		<p class="sub">
			El sankey mostra resultats laborals; els dos blocs anteriors mostren com
			pesen aquests resultats en la vida real. Aquest tancament et recorda
			que res del que s'ha descrit és inevitable: tot prové d'una <em>configuració
			política</em> que es pot canviar, tant individualment com col·lectivament.
		</p>
	</header>

	<aside class="hope">
		<p class="hope-title">El camí cap a {targetLabel}</p>
		<p class="synthesis">
			Tries un itinerari, sí, però no el tries sol. Cada decisió formativa la pots
			acompanyar de tres palanques que la majoria de joves no fan servir per
			desconeixement:
		</p>
		<ul>
			<li>
				<strong>Demana orientació pública.</strong> El SOC i el teu institut/universitat
				ofereixen cita gratuïta amb un orientador. La pots tenir abans de 15 dies.
				<a href="https://serveiocupacio.gencat.cat" target="_blank" rel="noreferrer">serveiocupacio.gencat.cat</a>
			</li>
			<li>
				<strong>Sol·licita totes les beques compatibles.</strong> AGAUR (Generalitat),
				MEFP (estat), Equitat (universitats públiques) i Erasmus+. Sovint es poden
				combinar i fan que el cost real d'un grau sigui assumible.
				<a href="https://agaur.gencat.cat" target="_blank" rel="noreferrer">agaur.gencat.cat</a>
			</li>
			<li>
				<strong>Construeix xarxa abans de necessitar-la.</strong> Un sindicat jove
				(<a href="https://www.ccoo.cat/joves" target="_blank" rel="noreferrer">CCOO Joves</a>),
				una associació professional, una colla d'activistes per l'habitatge
				(<a href="https://sindicatdellogateres.org" target="_blank" rel="noreferrer">Sindicat de Llogateres</a>).
				No esperis a tenir el problema per buscar la xarxa.
			</li>
		</ul>
		<p class="rally">
			Aquests itineraris són mapes, no destins. Els resultats que mostra l'atles són
			els que han passat fins ara amb les regles del joc actuals: si vols canviar-los,
			caldrà jugar a un altre joc.
		</p>
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
	}

	.sub em {
		color: var(--accent-warm);
		font-style: italic;
	}

	.synthesis {
		font-size: var(--fs-small);
		line-height: 1.5;
		color: var(--ink-secondary);
		margin-bottom: var(--sp-2);
	}

	.rally {
		margin-top: var(--sp-3);
		padding-top: var(--sp-3);
		border-top: 1px dashed color-mix(in srgb, var(--accent-warm) 35%, var(--border-default));
		font-size: var(--fs-small);
		font-style: italic;
		color: var(--ink-primary);
		line-height: 1.5;
	}

	.hope li strong {
		color: var(--ink-primary);
	}

	.hope {
		margin-top: var(--sp-2);
		padding: var(--sp-4);
		background: color-mix(in srgb, var(--accent-warm) 8%, transparent);
		border: 1px solid color-mix(in srgb, var(--accent-warm) 22%, var(--border-default));
		border-radius: var(--radius-md);
	}

	.hope-title {
		font-weight: 700;
		font-size: var(--fs-body);
		margin-bottom: var(--sp-3);
		color: var(--accent-warm);
	}

	.hope ul {
		list-style: none;
		padding-left: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}

	.hope li {
		font-size: var(--fs-small);
		line-height: 1.5;
		color: var(--ink-secondary);
		padding-left: var(--sp-4);
		position: relative;
	}

	.hope li::before {
		content: '→';
		position: absolute;
		left: 0;
		top: 0;
		color: var(--accent-warm);
		font-family: var(--font-mono);
	}

	.hope a {
		color: var(--accent-warm);
		text-decoration: underline;
		text-underline-offset: 2px;
	}
</style>
