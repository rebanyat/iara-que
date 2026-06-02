"""Export a slim occupations.json the client loads to power the search.

We read the ESCO occupations + ISCO groups parquets, derive the ISCO-1 root
of every occupation (first digit of the 4-digit ISCO code), and write one
record per occupation containing the fields needed for the FlexSearch index
and the dropdown items.

Schema (per record):
  id     short uuid (last segment of conceptUri)
  label  preferred label (Spanish, gender-doubled by ESCO)
  alt    list of up to 3 alternative labels (lowercased, dedup'd)
  isco4  ISCO 4-digit code as string
  isco1  ISCO 1-digit major group (so the sankey can map straight to its node)
  iscoLabel  Spanish label of the ISCO group at the most specific level we know
"""
from __future__ import annotations

import re

import pandas as pd

from lib import CACHE_DIR, DATA_DIR, banner, log, require, write_json


GENDERED_SLASH = re.compile(r"\s*/\s*")


def _short_id(uri: str) -> str:
    return uri.rstrip("/").rsplit("/", 1)[-1]


def _drop_gendered_dup(label: str) -> str:
    """ESCO labels are 'director técnico/directora técnica'; we keep the first half."""
    if "/" in label:
        return GENDERED_SLASH.split(label, maxsplit=1)[0].strip()
    return label.strip()


def _split_alt(s: object) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    parts = [p.strip() for p in s.replace("|", "\n").split("\n") if p.strip()]
    # Deduplicate while preserving order; cap at 3
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
        if len(out) >= 3:
            break
    return out


def main() -> None:
    banner("06 · occupations.json")

    occ_path = CACHE_DIR / "esco_occupations.parquet"
    require(occ_path.exists(), "run 01_parse_esco.py first")
    occ = pd.read_parquet(occ_path)

    isco_path = CACHE_DIR / "esco_isco_groups.parquet"
    isco_lookup: dict[str, str] = {}
    if isco_path.exists():
        isco = pd.read_parquet(isco_path)
        for _, r in isco.iterrows():
            code = str(r["code"]).strip()
            label = str(r["label"]).strip()
            if code and label:
                isco_lookup[code] = label

    def best_isco_label(code: str) -> str:
        # Walk from the most specific 4-digit code up to ISCO-1
        for k in (code, code[:3], code[:2], code[:1]):
            if k in isco_lookup:
                return isco_lookup[k]
        return ""

    records: list[dict] = []
    for _, r in occ.iterrows():
        uri = str(r["uri"])
        isco4 = str(r["isco"]).strip()
        if not isco4 or not isco4[:1].isdigit():
            continue
        label = _drop_gendered_dup(str(r["label"]))
        alt = [_drop_gendered_dup(a) for a in _split_alt(r["alt"])]
        records.append(
            {
                "id": _short_id(uri),
                "label": label,
                "alt": alt,
                "isco4": isco4,
                "isco1": isco4[:1],
                "iscoLabel": best_isco_label(isco4),
            }
        )

    # Sort alphabetically by label for stable client-side display
    records.sort(key=lambda r: r["label"].lower())

    out = DATA_DIR / "occupations.json"
    write_json(records, out)

    # ── sanity ──────────────────────────────────────────────────────────
    print()
    by_isco1 = pd.Series([r["isco1"] for r in records]).value_counts().sort_index()
    log(f"sanity ✓ — {len(records):,} occupations exported")
    log(f"ISCO-1 distribution: {dict(by_isco1)}")
    sample = [r["label"] for r in records if "ontaner" in r["label"].lower() or "ontanero" in r["label"].lower()][:5]
    log(f"sample (fontaner-like): {sample}")


if __name__ == "__main__":
    main()
