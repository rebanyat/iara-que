<svelte:head>
  <title>Metodologia — I ara, què?</title>
</svelte:head>

<section class="container doc">
  <p class="eyebrow">com s'ha fet</p>
  <h1>Metodologia</h1>
  <p class="lede">
    Aquest atles és una composició honesta de dades públiques agregades. No té
    microdada ni cap pretensió predictiva — és una eina d'exploració per a
    orientadors, famílies i estudiants.
  </p>

  <h2 id="fonts">Fonts de dades</h2>
  <ul>
    <li>
      <strong>AQU Catalunya</strong> — Enquesta d'inserció laboral
      universitària, informes públics 2014, 2017, 2020, 2023. Aporten taxes
      d'ocupació, adequació, salari modal i satisfacció per branca i
      universitat.
      <a
        href="https://www.aqu.cat/ca/estudis-analisis/insercio-laboral"
        rel="noopener">aqu.cat</a
      >
    </li>
    <li>
      <strong>Consell General de Cambres de Catalunya</strong> — Estudi
      d'inserció laboral dels ensenyaments professionals, 2022. Cobreix FP-GM i
      FP-GS per família professional.
      <a href="https://www.cambrescat.cat" rel="noopener">cambrescat.cat</a>
    </li>
    <li>
      <strong>Idescat</strong> — Estadística de l'ensenyament (universitari i no
      universitari) i taula d'inserció laboral de graduats universitaris (<code
        >ilgu</code
      >).
      <a href="https://www.idescat.cat" rel="noopener">idescat.cat</a>
    </li>
    <li>
      <strong>MEFP</strong> — Estadística estatal d'FP (matrícula per modalitat
      i titularitat).
      <a href="https://www.educacionfpydeportes.gob.es" rel="noopener"
        >educacionfpydeportes.gob.es</a
      >
    </li>
    <li>
      <strong>Observatori del Treball i Model Productiu (Generalitat)</strong> —
      Consultes interactives de contractació, atur i salaris per comarca.
      <em>Pendent</em>: substituir les xifres placeholder del mapa.
      <a href="https://observatoritreball.gencat.cat" rel="noopener"
        >observatoritreball.gencat.cat</a
      >
    </li>
    <li>
      <strong>SEPE</strong> — Estadística d'ocupació i contractes registrats,
      slice Catalunya.
      <a
        href="https://www.sepe.es/HomeSepe/que-es-el-sepe/estadisticas"
        rel="noopener">sepe.es</a
      >
    </li>
    <li>
      <strong>ESCO v1.2.1 (UE)</strong> — Taxonomia europea d'ocupacions i
      competències. Clau mestra del cercador (3.043 ocupacions indexades) i del
      mapeig branca → ISCO-1.
      <a href="https://esco.ec.europa.eu" rel="noopener">esco.ec.europa.eu</a>
    </li>
    <li>
      <strong>Wikidata</strong> — Camins educatius de figures icòniques (capa
      <em>il·lustrativa</em>) via SPARQL pública. Avui 2 ocupacions
      (astronauta i direcció d'empresa) retornen dades estables; l'endpoint
      públic ha tornat 502/504 a les 40 restants i es recuperaran a mesura
      que el servei sigui més estable.
      <a href="https://query.wikidata.org" rel="noopener">query.wikidata.org</a>
    </li>
  </ul>

  <h2 id="preparacio">Preparació de les dades</h2>
  <ol>
    <li>
      <strong>ETL Python</strong> a <code>/scripts</code>: parse de tots els
      CSV/XLS d'origen, conversió a parquet intermedi, generació final dels JSON
      que el client consumeix. Idempotent: <code>make data</code> reconstrueix tot.
    </li>
    <li>
      <strong>Volums</strong> (capes 0–3 del sankey): cohorts derivades d'Idescat
      AEC (secundària, universitari) i MEFP (FP-GM/GS presencial i a distància, share
      Catalunya ≈ 18%, programa biennal).
    </li>
    <li>
      <strong>Mètriques per branca</strong> (capa 3 i 4): proporcions de mostres
      d'AQU 2023 (graus + màsters) i Cambres 2022 (FP-GS + FP-GM) per assignar shares
      branca i salari / ocupació / adequació / split de gènere.
    </li>
    <li>
      <strong>Branca → ISCO-1</strong>: mapping curat amb un modificador per
      ISCO que conserva l'ordre econòmic (directius > científics > tècnics >
      administratius > …). La distribució outcome la determina la mitjana de la
      composta arribant a cada node ISCO.
    </li>
    <li>
      <strong>Provenance</strong>: cada aresta del sankey porta el
      <em>dataset</em>, la
      <em>wave</em> de l'enquesta i un flag <code>placeholder</code>. La vista
      en
      <a href="/?view=table">taula</a> permet auditar-les una a una.
    </li>
    <li>
      <strong>Conservació de massa</strong>: les arestes que entren a cada
      node intermedi sumen el mateix volum que les que en surten (tolerància de
      ±0,1 % per arrodoniments a enter). Les distribucions condicionals (% que
      titula, % que va a màster, % que entra a cada branca) s'apliquen sobre
      el volum realment arribat al node, no sobre fonts paral·leles.
    </li>
  </ol>

  <h2 id="metriques">Mètriques derivades</h2>
  <dl>
    <dt>Empleabilitat composta</dt>
    <dd>
      Combinació ponderada: 35 % taxa d'ocupació + 30 % % d'adequació + 25 %
      salari modal normalitzat a la franja 14k–40k € + 10 % % indefinits.
      Resultat ∈ [0, 1]. És el senyal per defecte del color de l'aresta.
    </dd>
    <dt>Bretxa salarial</dt>
    <dd>
      Salari modal masculí − salari modal femení, per branca i nivell de
      titulació.
    </dd>
    <dt>Velocitat d'inserció</dt>
    <dd>Mediana de mesos fins a la primera feina qualificada (AQU).</dd>
  </dl>

  <h2 id="glossari">Glossari</h2>
  <p>
    Termes que es repeteixen al llarg de l'atles, definits curts perquè
    qualsevol persona (orientadors, famílies, alumnat 4t ESO) pugui llegir-lo
    sense haver de googlejar.
  </p>
  <dl>
    <dt id="g-empleabilitat">Empleabilitat composta</dt>
    <dd>
      Índex propi (no oficial) que resumeix la qualitat laboral d'un camí en un
      sol número 0–1. Combina ocupació, adequació, salari i contracte indefinit.
      Veure
      <a href="#metriques">Mètriques derivades</a> per a la fórmula exacta.
    </dd>

    <dt id="g-salari-modal">Salari modal</dt>
    <dd>
      Tram salarial més freqüent dins d'una cohort (graduats d'una branca /
      titulació). No és la mitjana ni la mediana — és el <em>més habitual</em>.
      AQU el reporta perquè és menys distorsionat pels valors extrems que la
      mitjana.
    </dd>

    <dt id="g-adequacio">Adequació al títol</dt>
    <dd>
      % de persones graduades que treballen en una feina que exigeix el títol
      que tenen. Si treballes de cambrer amb un grau de filologia, no comptes
      com a "adequat". Mesura la sobrequalificació pràctica del mercat.
    </dd>

    <dt id="g-ocupacio">Taxa d'ocupació</dt>
    <dd>
      % de la cohort que té feina al moment de l'enquesta (3 anys després de
      graduar-se, AQU). Inclou autònoms i contractes parcials.
    </dd>

    <dt id="g-atur">Taxa d'atur</dt>
    <dd>
      % d'actius (persones que volen treballar) sense feina. Diferent de la
      d'ocupació perquè exclou els inactius (estudiants, cura, etc.).
    </dd>

    <dt id="g-branca">Branca</dt>
    <dd>
      Agrupació gran d'estudis. L'atles utilitza les 6 branques d'AQU: STEM,
      Salut, Socials i jurídiques, Humanitats i arts, Serveis, Indústria i
      construcció.
    </dd>

    <dt id="g-isco">ISCO-08</dt>
    <dd>
      Classificació Internacional Uniforme d'Ocupacions, de l'Organització
      Internacional del Treball (OIT). 10 grups grans (ISCO-1: directius,
      científics, tècnics, etc.). A iara és la capa "ocupació" del sankey.
    </dd>

    <dt id="g-esco">ESCO</dt>
    <dd>
      Classificació europea d'habilitats, competències, qualificacions i
      ocupacions. Versió detallada d'ISCO amb 3.043 ocupacions a Catalunya
      (cobertura aproximada). L'utilitzem al cercador "Vull ser…".
    </dd>

    <dt id="g-fp">FP-GM / FP-GS</dt>
    <dd>
      Formació Professional de Grau Mitjà (després d'ESO, durada 2 anys) i de
      Grau Superior (després de batxillerat o FP-GM, durada 2 anys). FP-GS dona
      accés directe a graus universitaris afins.
    </dd>

    <dt id="g-aqu">AQU Catalunya</dt>
    <dd>
      Agència per a la Qualitat del Sistema Universitari de Catalunya. Publica
      cada 3 anys l'enquesta d'inserció laboral dels graduats. Font principal de
      salari, ocupació i adequació al nostre atles.
    </dd>

    <dt id="g-idescat">Idescat</dt>
    <dd>
      Institut d'Estadística de Catalunya. Aporta les cohorts demogràfiques i
      les taules d'inserció laboral de graduats universitaris (ilgu).
    </dd>

    <dt id="g-mefp">MEFP</dt>
    <dd>
      Ministeri d'Educació, Formació Professional i Esports d'Espanya.
      Estadística estatal d'FP — matrícula per modalitat, titularitat i
      comunitat autònoma.
    </dd>

    <dt id="g-cambres">Consell de Cambres</dt>
    <dd>
      Consell General de Cambres de Catalunya. Estudi d'inserció laboral dels
      ensenyaments professionals (FP-GM i FP-GS) per famílies professionals.
      Anàleg de l'AQU per a FP.
    </dd>

    <dt id="g-sepe">SEPE</dt>
    <dd>
      Servei Públic d'Ocupació Estatal. Estadística mensual de contractació,
      atur registrat i sortides laborals per CCAA.
    </dd>

    <dt id="g-observatori">Observatori del Treball</dt>
    <dd>
      Servei de la Generalitat amb consultes interactives de contractació, atur
      i salaris per comarca. Origen de les dades de mapa territorial.
    </dd>

    <dt id="g-wikidata">Wikidata</dt>
    <dd>
      Base de dades col·laborativa lligada a Wikipedia. La capa "camins icònics"
      del cercador extrau les titulacions de figures notables (astronauta,
      Nobel, etc.) — és il·lustrativa, no estadística.
    </dd>

    <dt id="g-ipc">IPC (Índex de Preus de Consum)</dt>
    <dd>
      Mesura mensual de la variació de preus d'una cistella representativa,
      publicada per l'INE. L'utilitzem per convertir salaris nominals a €
      constants 2024 (toggle a
      <em>Evolució 2014→2023</em>).
    </dd>

    <dt id="g-poder">Poder adquisitiu</dt>
    <dd>
      Quantitat real de béns i serveis que pots comprar amb un sou. Cau quan els
      preus pugen més de pressa que el salari nominal. Els salaris reportats per
      AQU són nominals: a "Reality check" els relativitzem.
    </dd>

    <dt id="g-placeholder">Placeholder</dt>
    <dd>
      Etiqueta tècnica que marca valors estimats provisionalment perquè la font
      definitiva encara no està integrada. Avui el mapa comarcal porta xifres
      sintetitzades per província; quan integrem l'Observatori del Treball
      s'eliminarà.
    </dd>
  </dl>

  <h2 id="dades-grolleres">Sobre la granularitat de les dades</h2>
  <p>
    Els salaris i taxes que veus al sankey són <strong
      >agregats per branca</strong
    >
    (AQU 2023, Cambres 2022). Això significa que una persona concreta amb un títol
    concret pot tenir un salari molt diferent del que llegim aquí — un graduat en
    Enginyeria Informàtica i una graduada en Filologia STEM apareixen al mateix node
    "STEM" amb la mateixa mètrica, encara que les realitats individuals divergeixen
    molt.
  </p>
  <p>
    Per atenuar aquest efecte, fer clic sobre una branca al sankey la desplega
    en 5–6 titulacions específiques (capes "↳" per a Enginyeria informàtica,
    Medicina, Dret, etc.) aplicant <em>multiplicadors</em> sobre la mètrica de
    la branca. Aquests multiplicadors són una <strong>aproximació</strong>
    basada en l'Annex per estudi dels informes AQU i no en una explotació per
    titulació de la microdada — AQU no publica aquesta resolució. Quan una
    administració publiqui dades per titulació desagregades amb sample
    suficient, el codi està preparat per substituir els multiplicadors per dades
    reals (camp <code>children</code> de cada node branca a
    <code>sankey.json</code>).
  </p>
  <p>
    Resumit: les xifres serveixen per <strong>comparar camins entre si</strong> i
    per entendre tendències; no per a pronosticar el sou d'una persona concreta.
    Per a això, parla amb un orientador del SOC o del teu institut.
  </p>

  <h2 id="biaixos">Biaixos i limitacions identificats</h2>
  <ul>
    <li>
      <strong>Biaix de no-resposta</strong>: les enquestes d'inserció arriben
      sobretot a qui ha trobat feina. Les taxes d'ocupació estan probablement
      <em>sobreestimades</em>.
    </li>
    <li>
      <strong>Biaix temporal</strong>: AQU mesura a 3 anys. No copsa
      trajectòries a 10+ anys ni el cost d'oportunitat acumulat.
    </li>
    <li>
      <strong>Biaix de desagregació</strong>: cel·les amb pocs casos se
      suprimeixen per anonimat. Algunes branques minoritàries no apareixen.
    </li>
    <li>
      <strong>Itineraris informals</strong>: autoformació, formació d'empresa i
      certificats no reglats no figuren en cap font, però ocupen una fracció
      rellevant del mercat.
    </li>
    <li>
      <strong>Biaix territorial</strong>: el mapa comarcal mostra estimacions
      per província interpolades a comarca, perquè l'Observatori del Treball
      encara no està integrat. Per això les diferències intra-província
      s'aplanen.
    </li>
    <li>
      <strong>Wikidata</strong>: representa figures notables
      (sobre-representació de perfils mediàtics). La capa està etiquetada com a
      <em>il·lustrativa, no estadística</em>.
    </li>
  </ul>

  <h2 id="ia">Ús d'intel·ligència artificial</h2>
  <p>
    Aquest projecte ha utilitzat assistència d'IA per a tasques de codi i
    d'esborrany de text, dins el marc que permet la UOC. Conforme al pla docent:
  </p>
  <ul>
    <li>
      <strong>Eines</strong>: Anthropic Claude, Google Gemini, Open AI ChatGPT,
      via l'interfície de programació, amb instruccions detallades pas a pas
      escrites per l'autor.
    </li>
    <li>
      <strong>Objectiu</strong>: accelerar el pipeline ETL i la implementació
      del front; esbossar primeres versions de microcopy i de la metodologia;
      informar sobre decissions de disseny i de pipeline.
    </li>
    <li>
      <strong>Procés de revisió</strong>: l'autor ha revisat manualment cada
      decisió de disseny, cada valor numèric introduït a les taules curades
      (AQU/Cambres) i cada interacció abans del commit. Cap visualització ha
      estat generada per IA.
    </li>
    <li>
      <strong>Detall i prompts</strong>: registre exhaustiu a
      <code>docs/ai_usage.md</code>
      del repositori.
    </li>
  </ul>

  <h2 id="repo">Codi font i llicència</h2>
  <p>
    Codi obert MIT a
    <a href="https://github.com/rebanyat/iara-que" rel="noopener"
      >github.com/rebanyat/iara-que</a
    >. Continguts i visualitzacions sota CC BY 4.0. Cada font de dades conserva
    la seva llicència original.
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
    scroll-margin-top: calc(var(--header-h) + var(--sp-3));
  }

  dt[id]::before {
    content: "§";
    font-family: var(--font-mono);
    color: var(--ink-muted);
    font-weight: 400;
    font-size: 0.8em;
    margin-right: var(--sp-2);
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
