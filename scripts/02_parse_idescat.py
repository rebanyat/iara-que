"""Parse Idescat CSVs (teaching + university) into a long-format parquet.

Source files use the `row;col;r;c;value;status` schema, where each row is a
single cell in a pivoted table. We melt them into a long table and tag the
file of origin so downstream code can pick the relevant slice.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from lib import CACHE_DIR, RAW_DIR, banner, log, require


TEACHING_DIR = RAW_DIR / "idescat_estadística ensenyament"
UNI_DIR = RAW_DIR / "idescat_universitari"

CURS_RE = re.compile(r"Curs\s+(\d{4})/(\d{2,4})")


def _parse_value(s: str) -> float | None:
    if not s or s in {"", ".."}:
        return None
    return float(s.replace(".", "").replace(",", "."))


def _curs_to_year(s: str) -> int | None:
    if not isinstance(s, str):
        return None
    m = CURS_RE.search(s)
    if not m:
        return None
    start = int(m.group(1))
    return start + 1  # convention: "Curs 2020/21" → 2021


def _load_one(path: Path, scope: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["row_label"] = df["row"].astype(str).str.strip('"')
    df["col_label"] = df["col"].astype(str).str.strip('"')
    df["value"] = df["value"].map(_parse_value)
    df["year"] = df["row_label"].map(_curs_to_year)
    df["source_file"] = path.name
    df["scope"] = scope
    return df[["scope", "source_file", "year", "row_label", "col_label", "value", "status"]]


def main() -> None:
    banner("02 · Idescat")

    teaching_files = sorted(TEACHING_DIR.glob("*.csv"))
    uni_files = sorted(UNI_DIR.glob("*.csv"))
    require(teaching_files or uni_files, "no Idescat CSVs found")

    frames = []
    for f in teaching_files:
        frames.append(_load_one(f, "teaching"))
    for f in uni_files:
        frames.append(_load_one(f, "university"))

    df = pd.concat(frames, ignore_index=True)
    out = CACHE_DIR / "idescat_long.parquet"
    df.to_parquet(out, index=False)
    log(f"merged: {len(df):,} rows across {len(frames)} CSV files → {out.name}")

    # --- a couple of derived tables that other scripts will lean on ---
    # 1) latest enrolment totals by stage (teaching)
    teaching = df[df["scope"] == "teaching"].copy()
    # "Curs 2023/24" Alumnes by educational level — first AEC table
    overview = teaching[
        teaching["source_file"].str.contains("aec-15712")
        & teaching["col_label"].isin(
            [
                "Alumnes",
                "Educació infantil",
                "Educació primària",
                "Educació secundària",
                "Ensenyament universitari",
            ]
        )
    ].copy()
    overview_out = CACHE_DIR / "idescat_teaching_overview.parquet"
    overview.to_parquet(overview_out, index=False)
    log(f"teaching overview: {len(overview):,} rows → {overview_out.name}")

    # 2) university totals Catalunya
    uni = df[df["scope"] == "university"].copy()
    uni_cat = uni[
        uni["source_file"].str.contains("ue-10098-1")
        & (uni["col_label"] == "Catalunya")
    ].copy()
    uni_out = CACHE_DIR / "idescat_university_total_cat.parquet"
    uni_cat.to_parquet(uni_out, index=False)
    log(f"university totals (Catalunya): {len(uni_cat):,} rows → {uni_out.name}")

    # 3) university by sex (basics-10370 → Homes/Dones/Total)
    uni_sex = uni[uni["source_file"].str.contains("basics-10370")].copy()
    uni_sex_out = CACHE_DIR / "idescat_university_by_sex.parquet"
    uni_sex.to_parquet(uni_sex_out, index=False)
    log(f"university by sex: {len(uni_sex):,} rows → {uni_sex_out.name}")

    # --- sanity ---
    print()
    last_uni_cat = uni_cat.dropna(subset=["value"]).sort_values("year").tail(1)
    if not last_uni_cat.empty:
        row = last_uni_cat.iloc[0]
        log(
            f"sanity ✓ — most recent uni Catalunya total = {int(row['value']):,} ({row['row_label']})"
        )


if __name__ == "__main__":
    main()
