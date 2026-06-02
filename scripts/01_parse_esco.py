"""Parse the already-extracted ESCO classification CSVs into parquet.

ESCO acts as the master taxonomy. We pull three slices we need:
  · occupations_es.csv          — 3k+ occupations with ISCO codes & labels
  · ISCOGroups_es.csv           — ISCO hierarchy (rollup keys)
  · broaderRelationsOccPillar_es.csv — occupation parent/child relations
"""
from __future__ import annotations

import pandas as pd

from lib import CACHE_DIR, RAW_DIR, banner, find_one, log, require


def main() -> None:
    banner("01 · ESCO")

    esco_dir = find_one(
        RAW_DIR / "ESCO",
        ["ESCO dataset*classification*es*csv", "ESCO*es*csv"],
    )
    require(esco_dir is not None and esco_dir.is_dir(), "extracted ESCO folder not found")
    assert esco_dir is not None
    log(f"source: {esco_dir.relative_to(RAW_DIR)}/")

    # --- occupations ---
    occ_csv = esco_dir / "occupations_es.csv"
    require(occ_csv.exists(), "occupations_es.csv missing")
    occ = pd.read_csv(occ_csv, dtype=str).fillna("")
    occ_keep = [
        c
        for c in [
            "conceptUri",
            "iscoGroup",
            "preferredLabel",
            "altLabels",
            "description",
        ]
        if c in occ.columns
    ]
    occ_clean = occ[occ_keep].rename(
        columns={
            "conceptUri": "uri",
            "iscoGroup": "isco",
            "preferredLabel": "label",
            "altLabels": "alt",
        }
    )
    occ_out = CACHE_DIR / "esco_occupations.parquet"
    occ_clean.to_parquet(occ_out, index=False)
    log(f"occupations: {len(occ_clean):,} rows → {occ_out.name}")

    # --- ISCO groups (hierarchy) ---
    isco_csv = esco_dir / "ISCOGroups_es.csv"
    if isco_csv.exists():
        isco = pd.read_csv(isco_csv, dtype=str).fillna("")
        keep = [c for c in ["code", "preferredLabel", "description"] if c in isco.columns]
        isco_clean = isco[keep].rename(columns={"preferredLabel": "label"})
        isco_out = CACHE_DIR / "esco_isco_groups.parquet"
        isco_clean.to_parquet(isco_out, index=False)
        log(f"ISCO groups: {len(isco_clean):,} rows → {isco_out.name}")

    # --- occupation broader relations (taxonomy edges) ---
    rel_csv = esco_dir / "broaderRelationsOccPillar_es.csv"
    if rel_csv.exists():
        rel = pd.read_csv(rel_csv, dtype=str).fillna("")
        rel_out = CACHE_DIR / "esco_occ_hierarchy.parquet"
        rel.to_parquet(rel_out, index=False)
        log(f"occupation hierarchy: {len(rel):,} rows → {rel_out.name}")

    # --- sanity ---
    print()
    log(f"sanity ✓ — occupations with ISCO code: {(occ_clean['isco'] != '').sum():,}")
    isco1 = sorted({c[:1] for c in occ_clean['isco'] if c and c[:1].isdigit()})
    log(f"ISCO-1 major groups represented: {len(isco1)} ({''.join(isco1)})")


if __name__ == "__main__":
    main()
