"""Parse MEFP national statistics into a tidy parquet.

MEFP files come in 7 nacional_0X.csv with 4 columns:
  · Titularidad del centro     (centre ownership)
  · Enseñanza                  (teaching level / track)
  · Variación con respecto al año anterior   (variable name)
  · Total                      (value)

The 'Variación' column actually multiplexes four series per row:
  - 'Datos curso 2024-25'
  - 'Datos curso 2023-24'
  - 'Variación absoluta'
  - 'Variación porcentual'

We pivot it so each row carries one (titularitat, ensenyança) tuple with the
current value, the previous value, and the variations.
"""
from __future__ import annotations

import re

import pandas as pd

from lib import CACHE_DIR, RAW_DIR, banner, log, require


MEFP_DIR = RAW_DIR / "MEFP"
CURS_RE = re.compile(r"Datos curso (\d{4})-(\d{2})")


def _parse_value(v: object) -> float | None:
    if not isinstance(v, str):
        return None
    v = v.strip()
    if not v or v in {".", "..", "-"}:
        return None
    cleaned = v.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def main() -> None:
    banner("03 · MEFP")

    csvs = sorted(MEFP_DIR.glob("nacional_*.csv"))
    require(csvs, "no MEFP CSVs found")

    frames = []
    for f in csvs:
        df = pd.read_csv(f, sep=";", dtype=str, encoding="utf-8-sig").fillna("")
        df.columns = [c.strip() for c in df.columns]
        df["source_file"] = f.name
        frames.append(df)

    raw = pd.concat(frames, ignore_index=True)
    log(f"loaded {len(raw):,} rows from {len(csvs)} CSV files")

    raw = raw.rename(
        columns={
            "Titularidad del centro": "titularitat",
            "Enseñanza": "ensenyança",
            "Variación con respecto al año anterior": "variable",
            "Total": "value_raw",
        }
    )
    raw["value"] = raw["value_raw"].map(_parse_value)

    # Detect "current year" label dynamically (most recent course)
    current_label = (
        raw["variable"].str.extract(r"^(Datos curso \d{4}-\d{2})$", expand=False).dropna().mode()
    )
    require(not current_label.empty, "could not detect 'current course' label")
    current_label = current_label.iloc[0]
    log(f"current course label: {current_label}")

    # Previous course = the other 'Datos curso ...' value
    prev_labels = (
        raw[raw["variable"].str.startswith("Datos curso", na=False) & (raw["variable"] != current_label)][
            "variable"
        ]
        .dropna()
        .unique()
    )
    require(len(prev_labels) >= 1, "could not detect previous-course label")
    prev_label = prev_labels[0]
    log(f"previous course label: {prev_label}")

    # Pivot: one row per (file, titularitat, ensenyança) with 4 columns
    pivoted = (
        raw.pivot_table(
            index=["source_file", "titularitat", "ensenyança"],
            columns="variable",
            values="value",
            aggfunc="first",
        )
        .reset_index()
    )

    pivoted = pivoted.rename(
        columns={
            current_label: "value_current",
            prev_label: "value_previous",
            "Variación absoluta": "var_absolute",
            "Variación porcentual": "var_pct",
        }
    )
    pivoted["current_course"] = current_label.replace("Datos curso ", "")
    pivoted["previous_course"] = prev_label.replace("Datos curso ", "")

    out_all = CACHE_DIR / "mefp_all.parquet"
    pivoted.to_parquet(out_all, index=False)
    log(f"pivoted: {len(pivoted):,} rows → {out_all.name}")

    # FP filter: keep rows whose 'ensenyança' clearly belongs to vocational tracks
    fp_keywords = [
        "C.F. Grado Medio",
        "C.F. Grado Superior",
        "Formación Profesional",
        "F.P. Básica",
        "FP Básica",
        "Ciclos Formativos",
    ]
    is_fp = pivoted["ensenyança"].str.contains("|".join(fp_keywords), regex=True, na=False)
    fp = pivoted[is_fp].copy()
    out_fp = CACHE_DIR / "mefp_fp.parquet"
    fp.to_parquet(out_fp, index=False)
    log(f"FP rows isolated: {len(fp):,} → {out_fp.name}")

    # Sanity: print top-line totals
    print()
    top_total = pivoted[(pivoted["ensenyança"] == "TOTAL") & (pivoted["titularitat"] == "TODOS LOS CENTROS")]
    if not top_total.empty:
        v = top_total["value_current"].dropna()
        if not v.empty:
            log(f"sanity ✓ — FP top-line total enrolment ({current_label}): {int(v.iloc[0]):,}")


if __name__ == "__main__":
    main()
