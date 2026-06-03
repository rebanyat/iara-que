"""Export a slim occupations.json the client loads to power the search.

We read the ESCO occupations + ISCO groups parquets, derive the ISCO-1 root
of every occupation (first digit of the 4-digit ISCO code), and write one
record per occupation containing the fields needed for the FlexSearch index
and the dropdown items.

Catalan layer (added 2026-06-03): ESCO only ships official EU languages, so
no Catalan dump is available. We overlay two hand-curated lexicons stored at
scripts/data/isco_ca.json (all 184 ISCO 1–3-digit groups) and
scripts/data/occupations_ca.json (one representative Catalan label per
ISCO-4-digit code, ~430 entries). When a Catalan label is available, we
promote it to `label` and demote the Spanish ESCO label into `alt` so the
FlexSearch index still finds Spanish queries.

Schema (per record):
  id        short uuid (last segment of conceptUri)
  label     preferred label (Catalan if curated, otherwise Spanish ESCO)
  alt       list of up to 3 alternative labels (lowercased, dedup'd)
  isco4     ISCO 4-digit code as string
  isco1     ISCO 1-digit major group (so the sankey can map straight to its node)
  iscoLabel Catalan label of the ISCO group at the most specific level we know
  langSource 'ca' if the canonical label is Catalan, 'es' otherwise (for QA)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from lib import CACHE_DIR, DATA_DIR, banner, log, require, write_json


GENDERED_SLASH = re.compile(r"\s*/\s*")
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_LEXICON = SCRIPT_DIR / "data"


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


def _load_lexicon(path: Path, key: str) -> dict[str, str]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        blob = json.load(f)
    raw = blob.get(key, {})
    out: dict[str, str] = {}
    for k, v in raw.items():
        if isinstance(v, str) and v.strip():
            out[str(k)] = v.strip()
    return out


def main() -> None:
    banner("06 · occupations.json")

    occ_path = CACHE_DIR / "esco_occupations.parquet"
    require(occ_path.exists(), "run 01_parse_esco.py first")
    occ = pd.read_parquet(occ_path)

    isco_path = CACHE_DIR / "esco_isco_groups.parquet"
    isco_lookup_es: dict[str, str] = {}
    if isco_path.exists():
        isco = pd.read_parquet(isco_path)
        for _, r in isco.iterrows():
            code = str(r["code"]).strip()
            label = str(r["label"]).strip()
            if code and label:
                isco_lookup_es[code] = label

    isco_lookup_ca = _load_lexicon(DATA_LEXICON / "isco_ca.json", "labels")
    occ_lookup_ca = _load_lexicon(DATA_LEXICON / "occupations_ca.json", "by_isco4")

    def best_isco_label(code: str) -> str:
        # Walk from the most specific 4-digit code up to ISCO-1, preferring CA.
        for k in (code, code[:3], code[:2], code[:1]):
            if k in isco_lookup_ca:
                return isco_lookup_ca[k]
        for k in (code, code[:3], code[:2], code[:1]):
            if k in isco_lookup_es:
                return isco_lookup_es[k]
        return ""

    records: list[dict] = []
    ca_count = 0
    for _, r in occ.iterrows():
        uri = str(r["uri"])
        isco4 = str(r["isco"]).strip()
        if not isco4 or not isco4[:1].isdigit():
            continue
        label_es = _drop_gendered_dup(str(r["label"]))
        alt_es = [_drop_gendered_dup(a) for a in _split_alt(r["alt"])]

        # Catalan promotion: if we have a hand-curated label for this ISCO-4,
        # use it as the canonical label and push the Spanish one into alt so
        # cross-language search still works.
        label_ca = occ_lookup_ca.get(isco4)
        if label_ca:
            label = label_ca
            alt = [label_es, *alt_es]
            lang_source = "ca"
            ca_count += 1
        else:
            label = label_es
            alt = alt_es
            lang_source = "es"

        # De-duplicate alt while preserving order; cap at 4 entries.
        seen: set[str] = set([label.lower()])
        alt_clean: list[str] = []
        for a in alt:
            k = a.lower()
            if k in seen:
                continue
            seen.add(k)
            alt_clean.append(a)
            if len(alt_clean) >= 4:
                break

        records.append(
            {
                "id": _short_id(uri),
                "label": label,
                "alt": alt_clean,
                "isco4": isco4,
                "isco1": isco4[:1],
                "iscoLabel": best_isco_label(isco4),
                "langSource": lang_source,
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
    log(f"Catalan canonical labels: {ca_count} ({ca_count / max(1, len(records)):.0%})")
    log(f"ISCO-1 distribution: {dict(by_isco1)}")
    sample = [
        r["label"]
        for r in records
        if "lampista" in r["label"].lower() or "fontaner" in r["label"].lower()
    ][:5]
    log(f"sample (lampista / fontaner): {sample}")


if __name__ == "__main__":
    main()
