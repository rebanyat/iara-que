<svelte:head>
	<title>Metodologia — I ara, què?</title>
</svelte:head>

<section class="container doc">
	<p class="eyebrow">com s'ha fet</p>
	<h1>Metodologia</h1>
	<p class="lede">
		Aquest atles és una composició honesta de dades públiques agregades. No té microdada ni
		cap pretensió predictiva — és una eina d'exploració per a orientadors, famílies i estudiants.
	</p>

	<h2 id="fonts">Fonts de dades</h2>
	<ul>
		<li>
			<strong>AQU Catalunya</strong> — Enquesta d'inserció laboral universitària, informes
			públics 2014, 2017, 2020, 2023. Aporten taxes d'ocupació, adequació, salari modal i
			satisfacció per branca i universitat.
			<a href="https://www.aqu.cat/ca/estudis-analisis/insercio-laboral" rel="noopener">aqu.cat</a>
		</li>
		<li>
			<strong>Consell General de Cambres de Catalunya</strong> — Estudi d'inserció laboral
			dels ensenyaments professionals, 2022. Cobreix FP-GM i FP-GS per família professional.
			<a href="https://www.cambrescat.cat" rel="noopener">cambrescat.cat</a>
		</li>
		<li>
			<strong>Idescat</strong> — Estadística de l'ensenyament (universitari i no universitari)
			i taula d'inserció laboral de graduats universitaris (<code>ilgu</code>).
			<a href="https://www.idescat.cat" rel="noopener">idescat.cat</a>
		</li>
		<li>
			<strong>MEFP</strong> — Estadística estatal d'FP (matrícula per modalitat i titularitat).
			<a href="https://www.educacionfpydeportes.gob.es" rel="noopener">educacionfpydeportes.gob.es</a>
		</li>
		<li>
			<strong>Observatori del Treball i Model Productiu (Generalitat)</strong> — Consultes
			interactives de contractació, atur i salaris per comarca. <em>Pendent</em>:
			substituir les xifres placeholder del mapa.
			<a href="https://observatoritreball.gencat.cat" rel="noopener">observatoritreball.gencat.cat</a>
		</li>
		<li>
			<strong>SEPE</strong> — Estadística d'ocupació i contractes registrats, slice Catalunya.
			<a href="https://www.sepe.es/HomeSepe/que-es-el-sepe/estadisticas" rel="noopener">sepe.es</a>
		</li>
		<li>
			<strong>ESCO v1.2.1 (UE)</strong> — Taxonomia europea d'ocupacions i competències. Clau
			mestra del cercador (3.043 ocupacions indexades) i del mapeig branca → ISCO-1.
			<a href="https://esco.ec.europa.eu" rel="noopener">esco.ec.europa.eu</a>
		</li>
		<li>
			<strong>Wikidata</strong> — Camins educatius de figures icòniques (capa
			<em>il·lustrativa</em>) via SPARQL pública. Avui 3 ocupacions retornen dades;
			l'endpoint públic ha tornat 502/504 a les altres 17 i es recuperaran a mesura
			que el servei sigui més estable.
			<a href="https://query.wikidata.org" rel="noopener">query.wikidata.org</a>
		</li>
	</ul>

	<h2 id="preparacio">Preparació de les dades</h2>
	<ol>
		<li>
			<strong>ETL Python</strong> a <code>/scripts</code>: parse de tots els CSV/XLS d'origen,
			conversió a parquet intermedi, generació final dels JSON que el client consumeix.
			Idempotent: <code>make data</code> reconstrueix tot.
		</li>
		<li>
			<strong>Volums</strong> (capes 0–3 del sankey): cohorts derivades d'Idescat AEC
			(secundària, universitari) i MEFP (FP-GM/GS presencial i a distància, share Catalunya
			≈ 18%, programa biennal).
		</li>
		<li>
			<strong>Mètriques per branca</strong> (capa 3 i 4): proporcions de mostres d'AQU 2023
			(graus + màsters) i Cambres 2022 (FP-GS + FP-GM) per assignar shares branca i salari /
			ocupació / adequació / split de gènere.
		</li>
		<li>
			<strong>Branca → ISCO-1</strong>: mapping curat amb un modificador per ISCO que
			conserva l'ordre econòmic (directius > científics > tècnics > administratius > …).
			La distribució outcome la determina la mitjana de la composta arribant a cada node ISCO.
		</li>
		<li>
			<strong>Provenance</strong>: cada aresta del sankey porta el <em>dataset</em>, la
			<em>wave</em> de l'enquesta i un flag <code>placeholder</code>. La vista en
			<a href="/?view=table">taula</a> permet auditar-les una a una.
		</li>
	</ol>

	<h2 id="metriques">Mètriques derivades</h2>
	<dl>
		<dt>Empleabilitat composta</dt>
		<dd>
			Combinació ponderada: 35 % taxa d'ocupació + 30 % % d'adequació + 25 % salari modal
			normalitzat a la franja 14k–40k € + 10 % % indefinits. Resultat ∈ [0, 1]. És el
			senyal per defecte del color de l'aresta.
		</dd>
		<dt>Bretxa salarial</dt>
		<dd>Salari modal masculí − salari modal femení, per branca i nivell de titulació.</dd>
		<dt>Velocitat d'inserció</dt>
		<dd>Mediana de mesos fins a la primera feina qualificada (AQU).</dd>
	</dl>

	<h2 id="biaixos">Biaixos i limitacions identificats</h2>
	<ul>
		<li>
			<strong>Biaix de no-resposta</strong>: les enquestes d'inserció arriben sobretot a
			qui ha trobat feina. Les taxes d'ocupació estan probablement <em>sobreestimades</em>.
		</li>
		<li>
			<strong>Biaix temporal</strong>: AQU mesura a 3 anys. No copsa trajectòries a 10+
			anys ni el cost d'oportunitat acumulat.
		</li>
		<li>
			<strong>Biaix de desagregació</strong>: cel·les amb pocs casos se suprimeixen per
			anonimat. Algunes branques minoritàries no apareixen.
		</li>
		<li>
			<strong>Itineraris informals</strong>: autoformació, formació d'empresa i certificats
			no reglats no figuren en cap font, però ocupen una fracció rellevant del mercat.
		</li>
		<li>
			<strong>Biaix territorial</strong>: el mapa actual <em>encara és placeholder</em>
			per provincia. La substitució per dades reals de l'Observatori és pendent.
		</li>
		<li>
			<strong>Wikidata</strong>: representa figures notables (sobre-representació de
			perfils mediàtics). La capa està etiquetada com a <em>il·lustrativa, no estadística</em>.
		</li>
	</ul>

	<h2 id="ia">Ús d'intel·ligència artificial</h2>
	<p>
		Aquest projecte ha utilitzat assistència d'IA per a tasques de codi i d'esborrany de
		text, dins el marc que permet la UOC. Conforme al pla docent:
	</p>
	<ul>
		<li>
			<strong>Eina</strong>: Anthropic Claude (model Opus 4.7), via l'interfície de
			programació, amb instruccions detallades pas a pas escrites per l'autor.
		</li>
		<li>
			<strong>Objectiu</strong>: accelerar el pipeline ETL i la implementació del front;
			esbossar primeres versions de microcopy i de la metodologia.
		</li>
		<li>
			<strong>Procés de revisió</strong>: l'autor ha revisat manualment cada decisió de
			disseny, cada valor numèric introduït a les taules curades (AQU/Cambres) i cada
			interacció abans del commit. Cap visualització ha estat generada per IA.
		</li>
		<li>
			<strong>Detall i prompts</strong>: registre exhaustiu a <code>docs/ai_usage.md</code>
			del repositori.
		</li>
	</ul>

	<h2 id="repo">Codi font i llicència</h2>
	<p>
		Codi obert MIT a
		<a href="https://github.com/rebanyat/iara-que" rel="noopener">github.com/rebanyat/iara-que</a>.
		Continguts i visualitzacions sota CC BY 4.0. Cada font de dades conserva la seva
		llicència original.
	</p>
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

	.lede {
		margin-top: var(--sp-5);
		font-size: 1.125rem;
		line-height: var(--lh-loose);
		color: var(--ink-secondary);
		max-width: 60ch;
	}

	h2 {
		font-size: var(--fs-h2);
		margin-top: var(--sp-8);
		margin-bottom: var(--sp-4);
	}

	ul,
	ol,
	dl {
		margin: 0;
		padding-left: var(--sp-5);
		color: var(--ink-secondary);
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
		line-height: var(--lh-loose);
	}

	dl {
		padding-left: 0;
	}

	dt {
		color: var(--ink-primary);
		font-weight: 600;
	}

	dd {
		margin: 0;
		margin-bottom: var(--sp-3);
	}

	strong {
		color: var(--ink-primary);
	}

	em {
		font-style: italic;
		color: var(--ink-secondary);
	}

	code {
		background: var(--bg-elev);
		padding: 0 var(--sp-1);
		border-radius: var(--radius-sm);
		font-size: 0.95em;
	}

	p {
		margin-top: var(--sp-3);
		color: var(--ink-secondary);
		line-height: var(--lh-loose);
	}
</style>
