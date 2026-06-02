# I ara, què? — Atles d'itineraris reals de formació i feina a Catalunya

> Projecte final de l'assignatura **Visualització de Dades** (Grau de Ciència de Dades Aplicada · UOC).
> Autor: **Ivan Rodríguez Quintana** · Curs 2026.

Eina pública i interactiva que reconstrueix els camins agregats de la formació a la feina a Catalunya, basada en dades obertes d'AQU, Cambres, Departament d'Educació, Idescat, MEFP, Observatori del Treball, SEPE, ESCO i Wikidata.

## Estructura

```
02_PR2/
├── app/                   # SvelteKit + D3 + Vercel
├── scripts/               # ETL Python (en construcció)
└── docs/                  # Cita de fonts i ús d'IA (en construcció)
```

## Executar localment

Requeriments: Node 20+, npm.

```bash
cd app
npm install
npm run dev
```

Obre http://localhost:5173.

## Llicència

- **Codi**: MIT (veure [`LICENSE`](./LICENSE)).
- **Continguts i visualitzacions**: CC BY 4.0.
- **Dades**: cada font conserva la seva llicència; veure `/metodologia` a l'app i `docs/data_sources.md`.

## Crèdits

Construït amb [SvelteKit](https://kit.svelte.dev), [D3.js](https://d3js.org), [TopoJSON](https://github.com/topojson) i [FlexSearch](https://github.com/nextapps-de/flexsearch). Desplegat amb [Vercel](https://vercel.com).
