# Fonts de dades

Inventari complet de les fonts utilitzades, amb cites formals i data
d'accés. La metodologia llegible per a l'usuari final viu a
`/metodologia` de la web.

| Font | Producte | Format | Llicència | Data d'accés | URL |
|---|---|---|---|---|---|
| **AQU Catalunya** | Enquesta d'inserció laboral universitària (informes 2014, 2017, 2020, 2023) | PDF | Obert amb citació requerida | abril 2026 | https://www.aqu.cat/ca/estudis-analisis/insercio-laboral |
| **Consell General de Cambres de Catalunya** | Estudi d'inserció laboral dels ensenyaments professionals 2022 | PDF | Públic | abril 2026 | https://www.cambrescat.cat |
| **Departament d'Educació (Generalitat de Catalunya)** | Estadística de l'ensenyament | CSV/web | Obert | abril 2026 | https://educacio.gencat.cat/ca/departament/estadistiques/ |
| **Idescat** | Estadística d'ensenyament, universitària i ilgu (inserció laboral graduats) | CSV (long-format) | Obert (Llei 23/1998, DL 15/2007) | abril 2026 | https://www.idescat.cat |
| **MEFP** | Estadística d'Ensenyament FP (`nacional_0X.csv`) | CSV | Obert (RISP, Reial Decret 1495/2011) | abril 2026 | https://www.educacionfpydeportes.gob.es |
| **Observatori del Treball i Model Productiu** | Consultes interactives de contractació, atur, salaris per comarca | Web interactiva (scrape) | Obert | abril 2026 | https://observatoritreball.gencat.cat |
| **SEPE** | Estadística d'ocupació i contractes registrats | XLS multi-fulla | Avís legal obert | abril 2026 | https://www.sepe.es/HomeSepe/que-es-el-sepe/estadisticas |
| **ESCO v1.2.1 (UE)** | Taxonomia ocupacions/competències | CSV (descompressat) | CC-BY 4.0 | 17 abril 2026 | https://esco.ec.europa.eu |
| **Wikidata** | Biografies de figures icòniques (P106, P69, P101, P21) | SPARQL JSON | CC0 | juny 2026 | https://query.wikidata.org |
| **OECD** | Education at a Glance | CSV | CC-BY-NC 4.0 | abril 2026 | https://www.oecd.org/education/education-at-a-glance/ |
| **sirisacademic / catalonia-cartography** | Comarques GeoJSON | GeoJSON | MIT-friendly | juny 2026 | https://github.com/sirisacademic/catalonia-cartography |

## Comunicacions institucionals

- **AQU Catalunya** (Núria Comet, 20-abr-2026): sol·licitud de microdata
  derivada al formulari oficial. Procés formal de setmanes — fora de
  finestra del projecte.
- **Consell de Cambres** (20-abr-2026): redirigeix al Departament
  d'Educació, que requereix sol·licitud formal — fora de finestra.
- **Departament d'Educació** (codi HQ4TNYLLW-1, 27-abr-2026): mateixa
  ruta.
- **Observatori del Treball** (codi GN5JWK3Q-1, 20-abr-2026): remet a
  les consultes interactives — usables sense formalitats.
- **Idescat** (Javier Nieto, 20-mai-2026): publica les sèries `ilgu`
  i les microdades EPA via INE.

## Mètriques derivades

- `composite_employability` = 0.35 · pct_employed + 0.30 · pct_adequate
  + 0.25 · salary_normalised + 0.10 · pct_indef, on
  `salary_normalised = clamp((salary − 14000) / (40000 − 14000), 0, 1)`.
- `gap` = salary_m − salary_f, per branca i nivell.
- ISCO-1 inferit de l'ESCO 4-digit code per partició dels nodes
  `isco__N` (0–9) del sankey.

## Reproducibilitat

Tot el pipeline és idempotent. Veure `scripts/README.md`:

```
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
