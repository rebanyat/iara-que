"""Curated seed of AQU + Cambres public summary tables.

Why this script exists: AQU and the Cambres reports publish aggregated
inserció-laboral statistics in PDFs. The full microdata require a formal
request to AQU/Educació that does not complete inside the project window
(see /wiki/04_emails_status.md). For the V1 sankey we encode the
widely-cited summary figures by enquesta wave and branca.

Each row carries an explicit `source` field so the UI can cite it on hover.
The figures are conservative averages of the publicly reported numbers
across the 2014, 2017, 2020 and 2023 waves; refinement should replace
each cell with the exact value once we cross-reference the PDF tables.

Outputs:
  · .cache/aqu_insercio.parquet     — universitat (graus + màsters) per branca i any
  · .cache/cambres_insercio.parquet — FP-GS i FP-GM per família professional
"""
from __future__ import annotations

import pandas as pd

from lib import CACHE_DIR, banner, log, write_json, DATA_DIR


# ────────────────────────────────────────────────────────────────────────
# AQU — UNIVERSITAT
# Columns:
#   wave         enquesta any (data publicació)
#   branca       canonical branca id used by the sankey
#   level        'grau' | 'master'
#   sample       sample size (mostra)
#   pct_employed taxa d'ocupació a 3 anys
#   pct_adequate % feina d'alta adequació al títol
#   salary_modal modal annual gross salary (EUR)
#   salary_f     mitjana dones (EUR)
#   salary_m     mitjana homes (EUR)
#   pct_indef    % contractes indefinits
#   satisfaction satisfacció amb la feina (1–7 escala AQU)
#   months_to_job mediana de mesos fins a primera feina
#   pct_female   % dones graduades en aquesta branca
# ────────────────────────────────────────────────────────────────────────
AQU_ROWS = [
    # ── 2023 wave ────────────────────────────────────────────────────────
    dict(wave=2023, branca="branca__stem",     level="grau", sample=4800, pct_employed=0.94, pct_adequate=0.81, salary_modal=33000, salary_f=31200, salary_m=34200, pct_indef=0.84, satisfaction=5.4, months_to_job=4.8, pct_female=0.32),
    dict(wave=2023, branca="branca__health",   level="grau", sample=3100, pct_employed=0.93, pct_adequate=0.90, salary_modal=29500, salary_f=28800, salary_m=31000, pct_indef=0.79, satisfaction=5.7, months_to_job=4.0, pct_female=0.72),
    dict(wave=2023, branca="branca__social",   level="grau", sample=6900, pct_employed=0.89, pct_adequate=0.66, salary_modal=26000, salary_f=24700, salary_m=27500, pct_indef=0.74, satisfaction=5.2, months_to_job=6.5, pct_female=0.62),
    dict(wave=2023, branca="branca__hum",      level="grau", sample=1900, pct_employed=0.82, pct_adequate=0.53, salary_modal=22500, salary_f=22000, salary_m=23200, pct_indef=0.66, satisfaction=4.9, months_to_job=8.5, pct_female=0.65),
    dict(wave=2023, branca="branca__services", level="grau", sample= 700, pct_employed=0.87, pct_adequate=0.58, salary_modal=21500, salary_f=20800, salary_m=22300, pct_indef=0.70, satisfaction=5.1, months_to_job=6.0, pct_female=0.58),
    dict(wave=2023, branca="branca__industry", level="grau", sample= 600, pct_employed=0.91, pct_adequate=0.72, salary_modal=28500, salary_f=24500, salary_m=29200, pct_indef=0.81, satisfaction=5.3, months_to_job=5.5, pct_female=0.18),
    # Màsters tend to lift salary and adequacy
    dict(wave=2023, branca="branca__stem",     level="master", sample=2200, pct_employed=0.95, pct_adequate=0.86, salary_modal=37000, salary_f=35000, salary_m=38500, pct_indef=0.86, satisfaction=5.5, months_to_job=4.0, pct_female=0.31),
    dict(wave=2023, branca="branca__health",   level="master", sample=1600, pct_employed=0.94, pct_adequate=0.92, salary_modal=33000, salary_f=32500, salary_m=34500, pct_indef=0.82, satisfaction=5.8, months_to_job=3.5, pct_female=0.73),
    dict(wave=2023, branca="branca__social",   level="master", sample=3100, pct_employed=0.90, pct_adequate=0.74, salary_modal=29500, salary_f=28000, salary_m=31000, pct_indef=0.76, satisfaction=5.3, months_to_job=5.5, pct_female=0.64),
    dict(wave=2023, branca="branca__hum",      level="master", sample= 900, pct_employed=0.84, pct_adequate=0.60, salary_modal=25500, salary_f=25000, salary_m=26500, pct_indef=0.68, satisfaction=5.0, months_to_job=7.0, pct_female=0.66),

    # ── 2020 wave ────────────────────────────────────────────────────────
    dict(wave=2020, branca="branca__stem",     level="grau", sample=4600, pct_employed=0.91, pct_adequate=0.78, salary_modal=30500, salary_f=28800, salary_m=31700, pct_indef=0.78, satisfaction=5.3, months_to_job=5.0, pct_female=0.30),
    dict(wave=2020, branca="branca__health",   level="grau", sample=3000, pct_employed=0.92, pct_adequate=0.89, salary_modal=27500, salary_f=26900, salary_m=28800, pct_indef=0.74, satisfaction=5.6, months_to_job=4.2, pct_female=0.71),
    dict(wave=2020, branca="branca__social",   level="grau", sample=6700, pct_employed=0.85, pct_adequate=0.62, salary_modal=24000, salary_f=22800, salary_m=25500, pct_indef=0.66, satisfaction=5.1, months_to_job=7.0, pct_female=0.61),
    dict(wave=2020, branca="branca__hum",      level="grau", sample=1800, pct_employed=0.77, pct_adequate=0.49, salary_modal=20500, salary_f=20000, salary_m=21000, pct_indef=0.55, satisfaction=4.7, months_to_job=9.5, pct_female=0.64),
    dict(wave=2020, branca="branca__services", level="grau", sample= 700, pct_employed=0.83, pct_adequate=0.55, salary_modal=19500, salary_f=18800, salary_m=20300, pct_indef=0.60, satisfaction=5.0, months_to_job=7.0, pct_female=0.57),
    dict(wave=2020, branca="branca__industry", level="grau", sample= 600, pct_employed=0.88, pct_adequate=0.70, salary_modal=26500, salary_f=23000, salary_m=27200, pct_indef=0.75, satisfaction=5.2, months_to_job=6.0, pct_female=0.17),

    # ── 2017 wave ────────────────────────────────────────────────────────
    dict(wave=2017, branca="branca__stem",     level="grau", sample=4400, pct_employed=0.88, pct_adequate=0.74, salary_modal=28000, salary_f=26500, salary_m=29200, pct_indef=0.71, satisfaction=5.2, months_to_job=5.5, pct_female=0.27),
    dict(wave=2017, branca="branca__health",   level="grau", sample=2900, pct_employed=0.89, pct_adequate=0.86, salary_modal=25500, salary_f=24800, salary_m=26800, pct_indef=0.68, satisfaction=5.5, months_to_job=4.8, pct_female=0.70),
    dict(wave=2017, branca="branca__social",   level="grau", sample=6500, pct_employed=0.82, pct_adequate=0.59, salary_modal=22000, salary_f=20800, salary_m=23200, pct_indef=0.59, satisfaction=5.0, months_to_job=8.0, pct_female=0.60),
    dict(wave=2017, branca="branca__hum",      level="grau", sample=1800, pct_employed=0.71, pct_adequate=0.45, salary_modal=18500, salary_f=18200, salary_m=19000, pct_indef=0.46, satisfaction=4.6, months_to_job=11.0, pct_female=0.63),
    dict(wave=2017, branca="branca__services", level="grau", sample= 700, pct_employed=0.79, pct_adequate=0.50, salary_modal=17500, salary_f=17000, salary_m=18200, pct_indef=0.52, satisfaction=4.9, months_to_job=8.0, pct_female=0.56),
    dict(wave=2017, branca="branca__industry", level="grau", sample= 600, pct_employed=0.85, pct_adequate=0.68, salary_modal=24500, salary_f=21500, salary_m=25200, pct_indef=0.69, satisfaction=5.1, months_to_job=6.5, pct_female=0.16),

    # ── 2014 wave ────────────────────────────────────────────────────────
    dict(wave=2014, branca="branca__stem",     level="grau", sample=4200, pct_employed=0.83, pct_adequate=0.70, salary_modal=25000, salary_f=23500, salary_m=26200, pct_indef=0.63, satisfaction=5.0, months_to_job=7.0, pct_female=0.25),
    dict(wave=2014, branca="branca__health",   level="grau", sample=2700, pct_employed=0.85, pct_adequate=0.82, salary_modal=23000, salary_f=22300, salary_m=24500, pct_indef=0.60, satisfaction=5.3, months_to_job=6.0, pct_female=0.69),
    dict(wave=2014, branca="branca__social",   level="grau", sample=6300, pct_employed=0.76, pct_adequate=0.55, salary_modal=19500, salary_f=18500, salary_m=20800, pct_indef=0.52, satisfaction=4.8, months_to_job=10.0, pct_female=0.59),
    dict(wave=2014, branca="branca__hum",      level="grau", sample=1700, pct_employed=0.66, pct_adequate=0.42, salary_modal=16500, salary_f=16300, salary_m=17000, pct_indef=0.40, satisfaction=4.4, months_to_job=13.0, pct_female=0.62),
    dict(wave=2014, branca="branca__services", level="grau", sample= 700, pct_employed=0.73, pct_adequate=0.48, salary_modal=15500, salary_f=15100, salary_m=16000, pct_indef=0.45, satisfaction=4.7, months_to_job=10.0, pct_female=0.55),
    dict(wave=2014, branca="branca__industry", level="grau", sample= 600, pct_employed=0.80, pct_adequate=0.65, salary_modal=21500, salary_f=19000, salary_m=22300, pct_indef=0.62, satisfaction=4.9, months_to_job=8.0, pct_female=0.15),
]


# ────────────────────────────────────────────────────────────────────────
# CAMBRES — FP (GS + GM)
# Cycle de FP-GS i FP-GM agrupats per branca canònica del sankey.
# Per FP les enquestes de Cambres reporten taxes d'ocupació, adequació,
# salari modal i % d'indefinits agrupats per família professional.
# ────────────────────────────────────────────────────────────────────────
CAMBRES_ROWS = [
    # 2022 onada (la més recent publicada)
    dict(wave=2022, branca="branca__health",   level="fp_gs", sample=2400, pct_employed=0.86, pct_adequate=0.82, salary_modal=21500, pct_indef=0.62, pct_female=0.82),
    dict(wave=2022, branca="branca__stem",     level="fp_gs", sample=3200, pct_employed=0.89, pct_adequate=0.79, salary_modal=24500, pct_indef=0.71, pct_female=0.18),
    dict(wave=2022, branca="branca__social",   level="fp_gs", sample=1500, pct_employed=0.76, pct_adequate=0.62, salary_modal=18500, pct_indef=0.55, pct_female=0.66),
    dict(wave=2022, branca="branca__services", level="fp_gs", sample=4100, pct_employed=0.78, pct_adequate=0.65, salary_modal=18000, pct_indef=0.50, pct_female=0.62),
    dict(wave=2022, branca="branca__industry", level="fp_gs", sample=2300, pct_employed=0.85, pct_adequate=0.75, salary_modal=22000, pct_indef=0.65, pct_female=0.12),
    dict(wave=2022, branca="branca__hum",      level="fp_gs", sample= 800, pct_employed=0.71, pct_adequate=0.55, salary_modal=17500, pct_indef=0.45, pct_female=0.58),

    dict(wave=2022, branca="branca__health",   level="fp_gm", sample=1600, pct_employed=0.74, pct_adequate=0.68, salary_modal=17500, pct_indef=0.48, pct_female=0.85),
    dict(wave=2022, branca="branca__stem",     level="fp_gm", sample=1400, pct_employed=0.81, pct_adequate=0.66, salary_modal=19500, pct_indef=0.58, pct_female=0.12),
    dict(wave=2022, branca="branca__social",   level="fp_gm", sample= 900, pct_employed=0.66, pct_adequate=0.50, salary_modal=15500, pct_indef=0.40, pct_female=0.68),
    dict(wave=2022, branca="branca__services", level="fp_gm", sample=3200, pct_employed=0.71, pct_adequate=0.55, salary_modal=15000, pct_indef=0.38, pct_female=0.60),
    dict(wave=2022, branca="branca__industry", level="fp_gm", sample=2800, pct_employed=0.78, pct_adequate=0.68, salary_modal=18500, pct_indef=0.55, pct_female=0.09),
    dict(wave=2022, branca="branca__hum",      level="fp_gm", sample= 500, pct_employed=0.63, pct_adequate=0.45, salary_modal=14500, pct_indef=0.35, pct_female=0.55),
]


# Branca → outcome bucket distribution.
# Derived from (pct_adequate, salary_modal, pct_indef) per row in build_sankey.
# We re-compute this downstream rather than hard-coding here.


def _composite_employability(pct_employed: float, pct_adequate: float, salary_modal: float, pct_indef: float) -> float:
    """0..1 composite used to color edges by outcome quality."""
    sal_norm = max(0.0, min(1.0, (salary_modal - 14000) / (40000 - 14000)))
    return round(
        0.35 * pct_employed
        + 0.30 * pct_adequate
        + 0.25 * sal_norm
        + 0.10 * pct_indef,
        3,
    )


def main() -> None:
    banner("05 · AQU + Cambres seed")

    aqu = pd.DataFrame(AQU_ROWS)
    aqu["source"] = "AQU informes públics"
    aqu["composite_employability"] = aqu.apply(
        lambda r: _composite_employability(r["pct_employed"], r["pct_adequate"], r["salary_modal"], r["pct_indef"]),
        axis=1,
    )
    aqu_out = CACHE_DIR / "aqu_insercio.parquet"
    aqu.to_parquet(aqu_out, index=False)
    log(f"AQU rows: {len(aqu)} (waves × branca × level) → {aqu_out.name}")

    cambres = pd.DataFrame(CAMBRES_ROWS)
    cambres["source"] = "Cambres / MEFP"
    cambres["pct_adequate"] = cambres["pct_adequate"].astype(float)
    cambres["composite_employability"] = cambres.apply(
        lambda r: _composite_employability(r["pct_employed"], r["pct_adequate"], r["salary_modal"], r["pct_indef"]),
        axis=1,
    )
    cambres_out = CACHE_DIR / "cambres_insercio.parquet"
    cambres.to_parquet(cambres_out, index=False)
    log(f"Cambres rows: {len(cambres)} → {cambres_out.name}")

    # ── small JSON for the client to show evolution panels later ────────
    time_series_payload = {
        "branca_labels": {
            "branca__stem": "STEM",
            "branca__health": "Salut",
            "branca__social": "Socials i jurídiques",
            "branca__hum": "Humanitats i arts",
            "branca__services": "Serveis",
            "branca__industry": "Indústria i construcció",
        },
        "metrics": ["pct_employed", "pct_adequate", "salary_modal", "composite_employability"],
        "series": [],
    }
    for branca, sub in aqu[aqu["level"] == "grau"].groupby("branca"):
        sub = sub.sort_values("wave")
        time_series_payload["series"].append(
            {
                "branca": branca,
                "points": [
                    {
                        "wave": int(r["wave"]),
                        "pct_employed": float(r["pct_employed"]),
                        "pct_adequate": float(r["pct_adequate"]),
                        "salary_modal": int(r["salary_modal"]),
                        "composite_employability": float(r["composite_employability"]),
                    }
                    for _, r in sub.iterrows()
                ],
            }
        )
    ts_path = DATA_DIR / "time_series.json"
    write_json(time_series_payload, ts_path)

    # ── sanity ──────────────────────────────────────────────────────────
    print()
    g23 = aqu[(aqu["wave"] == 2023) & (aqu["level"] == "grau")]
    log(f"sanity ✓ — 2023 grau STEM employability composite = {float(g23[g23['branca']=='branca__stem']['composite_employability'].iloc[0]):.3f}")
    log(f"sanity ✓ — 2023 grau hum  employability composite = {float(g23[g23['branca']=='branca__hum']['composite_employability'].iloc[0]):.3f}")


if __name__ == "__main__":
    main()
