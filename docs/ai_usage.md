# Ús d'intel·ligència artificial

Conforme a la política de la UOC i al pla docent de l'assignatura
*Visualització de Dades*, aquest document registra l'ús d'IA al projecte
**"I ara, què?"**.

## Eina utilitzada

- **Models**: Anthropic Claude, Google Gemini, OpenAI Chat GPT
- **Modalitat**: instruccions detallades pas a pas escrites per l'autor,
  amb revisió manual del codi abans de qualsevol
  commit o publicació.

## Objectius

1. **Acceleració del pipeline ETL** — paral·lelitzar la lectura/parse
   dels CSV/XLS i d'altres arxius d'origen (Idescat, MEFP, SEPE, ESCO, AQU/Cambres).
2. **Implementació del front** (SvelteKit + D3) — components reutilitzables,
   stores reactius, transicions D3. Informació sobre les eines i consells sobre la metodologia.
3. **Esborrany de microcopy i metodologia** — primera versió de la pàgina
   `/metodologia`, headings dels panels, tooltips.

## Procés de revisió

- Cada decisió de disseny (paleta, layout, estats UI, comportament
  d'interacció) ha estat validada per l'autor.
- Cada valor numèric introduït a les taules curades d'AQU/Cambres
  (`scripts/05_seed_aqu_cambres.py`) ha estat revisat contra els informes
  públics i marcat amb provenança explícita al sankey (`meta.placeholder`,
  `meta.wave`, `meta.sourceDataset`).
- **Cap visualització ha estat generada per IA**: cada gràfic és codi
  escrit i revisat.
- L'autor manté l'autoria intel·lectual completa del projecte i és
  responsable de tot el contingut publicat.

## Exemple de prompts (representatiu)

> "Estic escrivint un script Python que parseja la carpeta MEFP
> (`nacional_01.csv`..`nacional_07.csv`). Els valors numèrics venen amb
> punt com a separador de milers (`389.982` = 389 982) i coma decimal.
> Vull pivotar 'Variación con respecto al año anterior' perquè cada
> fila tingui value_current / value_previous / var_absolute / var_pct.
> Escriu el script seguint les convencions de `lib.py` que ja existeix."

> "Aquest sankey amb d3-sankey llença 'missing: 0' al render. La layout
> està configurada amb .nodeId(d => d.id), però les links porten source
> i target convertits a índexs numèrics. Reconcilia."

> "El mapa coroplètic només mostra un bloc vermell amb el nom
> 'Baix Penedès'. La topojson té 41 geometries i transform present.
> Què està fallant?"

## Què NO ha fet la IA

- No ha pres cap decisió de scope sense aprovació explícita.
- No ha generat dades numèriques sense ser revisades contra una font.
- No ha publicat res a externes (commits, deploys, missatges) sense
  acció directa de l'autor.

## Citació

Es prega citar aquest projecte com:

> Rodríguez Quintana, I. (2026). *I ara, què? — Atles d'itineraris
> reals de formació i feina a Catalunya*. UOC, Visualització de Dades.
> https://iara-que.vercel.app
