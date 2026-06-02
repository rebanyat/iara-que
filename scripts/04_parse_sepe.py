"""Parse SEPE workbooks, keeping only Catalonia (province + autonomous community).

The SEPE workbooks use numbered sheets (e.g. '5.1', '5.3', '6.3'). Sheets
6.x onwards are 'DATOS POR COMUNIDADES AUTÓNOMAS Y PROVINCIAS'. We extract
two sheets we know are useful for the sankey and the side panels:

  · 6.3 (EMPLEO)    — demandas pendientes por nivel de estudios, por CCAA/prov.
  · 5.3 (EMPLEO)    — colocaciones por subgrupo de ocupación (ISCO-2), por CCAA/prov.

For each, we keep rows whose 'province' label matches Catalonia + its 4 provinces.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from lib import CACHE_DIR, RAW_DIR, banner, log, require

CAT_PROVINCES = {
    "BARCELONA",
    "GIRONA",
    "LLEIDA",
    "TARRAGONA",
    "CATALUÑA",
    "CATALUNYA",
}

EMPLEO_XLS = RAW_DIR / "ESTADISTICA DE EMPLEO.xls"
CONTRATOS_XLS = RAW_DIR / "ESTADISTICA_DE_CONTRATOS_MES.xls"


def _is_cat_label(s: object) -> bool:
    if not isinstance(s, str):
        return False
    return s.strip().upper() in CAT_PROVINCES


def _extract_table(xls_path: Path, sheet: str) -> pd.DataFrame:
    """Read a SEPE sheet, locate the header, and return a tidy DataFrame
    where the first non-numeric column is `province`."""
    raw = pd.read_excel(xls_path, sheet_name=sheet, header=None)
    # Find the header row: it contains 'TOTAL' as one of its values
    header_row = None
    for i in range(min(15, len(raw))):
        row_vals = [str(v).strip() for v in raw.iloc[i].dropna()]
        if any(v.upper() == "TOTAL" for v in row_vals):
            header_row = i
            break
    require(header_row is not None, f"could not locate header row in sheet {sheet}")
    headers = [str(v).strip() if isinstance(v, str) else f"col_{j}" for j, v in enumerate(raw.iloc[header_row])]
    body = raw.iloc[header_row + 1 :].copy()
    body.columns = headers
    # Find the province column (column with mostly text values)
    text_cols = [c for c in body.columns if body[c].apply(lambda v: isinstance(v, str)).mean() > 0.7]
    require(bool(text_cols), f"no text column found in sheet {sheet}")
    prov_col = text_cols[0]
    body = body.rename(columns={prov_col: "label"})
    body["label"] = body["label"].astype(str).str.strip()
    body = body.dropna(subset=["label"])
    return body


def main() -> None:
    banner("04 · SEPE")
    require(EMPLEO_XLS.exists(), f"missing {EMPLEO_XLS.name}")
    require(CONTRATOS_XLS.exists(), f"missing {CONTRATOS_XLS.name}")

    # --- 6.3: demand by educational level, CCAA + provinces ---
    log("loading EMPLEO 6.3 (demand by educational level)…")
    edu = _extract_table(EMPLEO_XLS, "6.3")
    edu_cat = edu[edu["label"].apply(_is_cat_label)].copy()
    edu_cat_out = CACHE_DIR / "sepe_demand_by_education_cat.parquet"
    edu_cat.to_parquet(edu_cat_out, index=False)
    log(f"Catalonia rows from 6.3: {len(edu_cat)} → {edu_cat_out.name}")

    # --- 5.3: placements by ISCO-2 subgroup, CCAA + provinces ---
    try:
        log("loading EMPLEO 5.3 (placements by ISCO-2)…")
        occ = _extract_table(EMPLEO_XLS, "5.3")
        occ_cat = occ[occ["label"].apply(_is_cat_label)].copy()
        occ_cat_out = CACHE_DIR / "sepe_placements_by_isco_cat.parquet"
        occ_cat.to_parquet(occ_cat_out, index=False)
        log(f"Catalonia rows from 5.3: {len(occ_cat)} → {occ_cat_out.name}")
    except Exception as e:
        log(f"skipped 5.3: {type(e).__name__}: {e}")

    # --- CONTRATOS 1.1M: monthly aggregate (used as time-series fallback) ---
    try:
        log("loading CONTRATOS 1.1M (monthly contracts)…")
        agg = pd.read_excel(CONTRATOS_XLS, sheet_name="1.1M", header=None)
        # Save raw — different shape, downstream can melt as needed
        out = CACHE_DIR / "sepe_contracts_1_1M_raw.parquet"
        agg.astype(str).to_parquet(out, index=False)
        log(f"contracts 1.1M raw: {agg.shape} → {out.name}")
    except Exception as e:
        log(f"skipped contracts 1.1M: {type(e).__name__}: {e}")

    # --- sanity ---
    print()
    if not edu_cat.empty:
        ccaa = edu_cat[edu_cat["label"].str.upper().isin({"CATALUÑA", "CATALUNYA"})]
        if not ccaa.empty and "TOTAL" in ccaa.columns:
            total = pd.to_numeric(ccaa["TOTAL"], errors="coerce").dropna()
            if not total.empty:
                log(f"sanity ✓ — Catalonia pending demand (TOTAL): {int(total.iloc[0]):,}")


if __name__ == "__main__":
    main()
