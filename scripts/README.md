# Data pipeline

Python ETL that reads the raw sources under `../../03_Datasets/` and writes the
visualization-ready JSON to `../app/static/data/`.

## One-shot

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python 01_parse_esco.py        # ESCO occupations + ISCO hierarchy
python 02_parse_idescat.py     # Teaching + university time series
python 03_parse_mefp.py        # National FP enrolment
python 04_parse_sepe.py        # Catalonia-only slice of SEPE
python 08_build_sankey.py      # Final sankey.json for the client
```

Intermediate parquets are written to `.cache/` (gitignored). The final JSON
artefacts that the client loads are committed under `../app/static/data/`.

## Outputs

| File | Built by | Consumed by |
|---|---|---|
| `../app/static/data/sankey.json` | `08_build_sankey.py` | `Sankey.svelte` |
| `../app/static/data/occupations.json` | (planned) `08_build_sankey.py` | `SearchBox.svelte` |
| `../app/static/data/comarques.topo.json` | (planned) external download | `ComarcaMap.svelte` |
