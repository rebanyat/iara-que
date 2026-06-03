# I ara, què? — Atles d'itineraris reals de formació i feina a Catalunya

> Projecte final de l'assignatura **Visualització de Dades**
> (Grau de Ciència de Dades Aplicada · UOC).
> Autor: **Ivan Rodríguez Quintana** · Curs 2026.

Eina pública i interactiva que reconstrueix els camins agregats de la
formació a la feina a Catalunya, basada en dades obertes d'AQU, Cambres,
Departament d'Educació, Idescat, MEFP, Observatori del Treball, SEPE,
ESCO i Wikidata.

**En producció**: <https://iara-que.vercel.app>

## Què ofereix

- Sankey llenç amb 35 nodes i ~120 arestes que cobreixen ESO → post-obligatòria
  → titulació → branca → ISCO-1 → outcome.
- Cercador **"Vull ser…"** sobre 3.043 ocupacions ESCO + capa il·lustrativa
  de figures icòniques de Wikidata.
- Filtres reactius per gènere i branca; mètrica de color commutable
  (composta, salari, % ocupats, % adequació).
- Side panels: top sortides ocupacionals, bretxa salarial F vs M, mapa
  per comarques i evolució 2014 → 2023.
- URL params persistents (compartibles) i vista en
  [taula HTML](https://iara-que.vercel.app/?view=table) per a lectors
  de pantalla.

## Estructura del repositori

```
02_PR2/
├── app/                # SvelteKit 2 + Svelte 5 (runes) + D3 + Vercel
├── scripts/            # ETL Python (pandas + topojson + requests)
├── docs/               # ai_usage.md + data_sources.md
└── README.md
```

## Executar localment

Requeriments: Node 20+ i Python 3.13+.

### App

```bash
cd app
npm install
npm run dev          # http://localhost:5173
npm run build        # producció (adapter-vercel)
npm run check        # svelte-check
```

### Pipeline de dades

```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python 01_parse_esco.py
python 02_parse_idescat.py
python 03_parse_mefp.py
python 04_parse_sepe.py
python 05_seed_aqu_cambres.py
python 06_export_occupations.py
python 08_build_sankey.py
python 09_build_comarques.py
python 10_query_wikidata.py
```

Cada script torna a generar els JSON sota `app/static/data/`.

## Llicència

- **Codi** — MIT ([`LICENSE`](./LICENSE)).
- **Continguts, microcopy, visualitzacions** — CC BY 4.0.
- **Dades** — cada font conserva la seva llicència, detall a
  [`docs/data_sources.md`](./docs/data_sources.md) i a `/metodologia` de l'app.

## Ús d'IA

Aquest projecte ha incorporat assistència d'IA (Claude) dins del marc que
permet la UOC. Detall complet i procés de revisió a
[`docs/ai_usage.md`](./docs/ai_usage.md).

## Crèdits

Construït amb [SvelteKit](https://kit.svelte.dev) + [D3.js](https://d3js.org)
+ [TopoJSON](https://github.com/topojson) + [FlexSearch](https://github.com/nextapps-de/flexsearch),
desplegat a [Vercel](https://vercel.com). Topojson de comarques derivat de
[sirisacademic/catalonia-cartography](https://github.com/sirisacademic/catalonia-cartography).

---

In English: an open atlas of formative and labour itineraries in Catalonia,
built for orientation professionals. Public data, MIT code, see
[`docs/`](./docs/) for sources and methodology.
