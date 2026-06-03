"""Build wikidata_icons.json with educational paths of icon professions.

We curate ~20 Q-IDs covering the full spectrum from oficis to academic-elite
careers. For each one we run a SPARQL query that returns up to N persons with
the occupation, their educated-at institutions (P69), their fields of work
(P101) and their gender (P21). We aggregate by label so the dropdown in the
SearchBox can show 'top educations / top fields' for each icon path.

The output is a small JSON keyed by ESCO-style isco1 so the sankey can map
each icon to its 'isco__N' major group via the same overlay logic the ESCO
search already uses.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import requests

from lib import CACHE_DIR, DATA_DIR, banner, log


SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = (
    "iara-que/0.1 (https://iara-que.vercel.app; ivanrodqui@gmail.com) "
    "python-requests/2"
)
CACHE_FILE = CACHE_DIR / "wikidata_icons_raw.json"


@dataclass
class IconSpec:
    qid: str  # Wikidata occupation id
    label: str  # display label
    isco1: str  # ISCO-1 major group ('0'..'9')
    isco_label: str  # short ISCO label used in side panels
    limit: int = 200  # max persons fetched
    notes: list[str] = field(default_factory=list)


ICONS: list[IconSpec] = [
    IconSpec("Q11631", "Astronauta", "2", "Professionals científics", 200),
    IconSpec("Q901", "Científic/a", "2", "Professionals científics", 250),
    IconSpec("Q170790", "Matemàtic/a", "2", "Professionals científics", 250),
    IconSpec("Q169470", "Físic/a", "2", "Professionals científics", 250),
    IconSpec("Q593644", "Investigador/a en IA", "2", "Professionals científics", 200),
    IconSpec("Q4964182", "Filòsof/a", "2", "Professionals científics", 200),
    IconSpec("Q36180", "Escriptor/a", "2", "Professionals científics", 300),
    IconSpec("Q47064", "Cineasta", "2", "Professionals científics", 200),
    IconSpec("Q177220", "Cantant", "3", "Tècnics i suport", 250),
    IconSpec("Q1028181", "Pintor/a", "3", "Tècnics i suport", 200),
    IconSpec("Q1622272", "Professor/a universitari", "2", "Professionals científics", 250),
    IconSpec("Q37226", "Mestre/a d'escola", "2", "Professionals científics", 200),
    IconSpec("Q39631", "Metge/metgessa", "2", "Professionals científics", 250),
    IconSpec("Q1933", "Infermer/a", "2", "Professionals científics", 200),
    IconSpec("Q40348", "Advocat/da", "2", "Professionals científics", 250),
    IconSpec("Q82955", "Polític/a", "1", "Directius i gerents", 250),
    IconSpec("Q484876", "CEO / direcció d'empresa", "1", "Directius i gerents", 250),
    IconSpec("Q11774891", "Enginyer/a", "2", "Professionals científics", 250),
    IconSpec("Q183733", "Fontaner/a", "7", "Artesans i oficis", 100),
    IconSpec("Q937857", "Futbolista professional", "3", "Tècnics i suport", 250),
]


SPARQL_TEMPLATE = """
SELECT
  (SAMPLE(?personLabel) AS ?personLabel)
  (SAMPLE(?genderLabel) AS ?genderLabel)
  (GROUP_CONCAT(DISTINCT ?eduLabel; separator="¦") AS ?eduLabels)
  (GROUP_CONCAT(DISTINCT ?fieldLabel; separator="¦") AS ?fieldLabels)
WHERE {{
  ?person wdt:P106 wd:{qid}.
  OPTIONAL {{
    ?person wdt:P69 ?edu.
    ?edu rdfs:label ?eduLabel.
    FILTER(LANG(?eduLabel) IN ("ca","es","en"))
  }}
  OPTIONAL {{
    ?person wdt:P101 ?field.
    ?field rdfs:label ?fieldLabel.
    FILTER(LANG(?fieldLabel) IN ("ca","es","en"))
  }}
  OPTIONAL {{
    ?person wdt:P21 ?gender.
    ?gender rdfs:label ?genderLabel.
    FILTER(LANG(?genderLabel) = "en")
  }}
  ?person rdfs:label ?personLabel.
  FILTER(LANG(?personLabel) IN ("ca","es","en"))
}}
GROUP BY ?person
LIMIT {limit}
""".strip()


def _query_one(spec: IconSpec) -> dict[str, Any]:
    log(f"querying {spec.label} ({spec.qid}) …")
    # Smaller LIMIT and retries with backoff to survive a rate-limited endpoint
    limit = min(spec.limit, 100)
    query = SPARQL_TEMPLATE.format(qid=spec.qid, limit=limit)
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}

    delays = [0, 8, 20, 45]
    for attempt, delay in enumerate(delays):
        if delay:
            time.sleep(delay)
        try:
            res = requests.post(
                SPARQL_URL,
                data={"query": query},
                headers=headers,
                timeout=90,
            )
            if res.status_code == 429:
                retry_after = int(res.headers.get("Retry-After", "30"))
                log(f"  · 429 throttled, sleeping {retry_after}s")
                time.sleep(retry_after)
                continue
            res.raise_for_status()
            return res.json()
        except Exception as e:
            log(f"  ✗ attempt {attempt + 1}/{len(delays)} {type(e).__name__}: {e}")
    return {"results": {"bindings": []}}


def _load_cache() -> dict[str, dict]:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return {}


def _save_cache(cache: dict[str, dict]) -> None:
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False))


def _summarise(spec: IconSpec, raw: dict[str, Any]) -> dict[str, Any]:
    bindings = raw.get("results", {}).get("bindings", [])
    edu_counter: Counter[str] = Counter()
    field_counter: Counter[str] = Counter()
    gender_counter: Counter[str] = Counter()
    sample_people: list[str] = []

    for b in bindings:
        label = (b.get("personLabel", {}) or {}).get("value")
        if label and label not in sample_people:
            sample_people.append(label)

        gender = (b.get("genderLabel", {}) or {}).get("value")
        if gender:
            gender_counter[gender.lower()] += 1

        for raw_value, counter in (
            (b.get("eduLabels", {}).get("value"), edu_counter),
            (b.get("fieldLabels", {}).get("value"), field_counter),
        ):
            if not raw_value:
                continue
            for piece in raw_value.split("¦"):
                p = piece.strip()
                if not p:
                    continue
                # Drop pure Q-ids that fall through
                if re.fullmatch(r"Q\d+", p):
                    continue
                counter[p] += 1

    def _top(counter: Counter[str], n: int = 6) -> list[dict[str, int]]:
        return [{"label": l, "count": c} for l, c in counter.most_common(n)]

    f = gender_counter.get("female", 0)
    m = gender_counter.get("male", 0)
    nb = gender_counter.get("non-binary", 0) + gender_counter.get("queer", 0)
    total_gender = f + m + nb
    gender_ratio = (
        {
            "F": round(f / total_gender, 3),
            "M": round(m / total_gender, 3),
            "NB": round(nb / total_gender, 3),
        }
        if total_gender > 0
        else None
    )

    return {
        "id": spec.qid,
        "label": spec.label,
        "isco1": spec.isco1,
        "iscoLabel": spec.isco_label,
        "count": len(bindings),
        "topEducations": _top(edu_counter, 6),
        "topFields": _top(field_counter, 6),
        "genderRatio": gender_ratio,
        "samplePeople": sample_people[:6],
        "source": "wikidata",
    }


def main() -> None:
    banner("10 · wikidata icons")

    cache = _load_cache()
    icons_summary: list[dict[str, Any]] = []

    for spec in ICONS:
        raw = cache.get(spec.qid)
        # Re-query if cached entry is empty (likely failed previous attempt)
        empty = raw is None or not raw.get("results", {}).get("bindings")
        if empty:
            raw = _query_one(spec)
            cache[spec.qid] = raw
            _save_cache(cache)
            time.sleep(3.0)  # be polite with the public endpoint
        icons_summary.append(_summarise(spec, raw))

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "icons": icons_summary,
    }
    out_path = DATA_DIR / "wikidata_icons.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False))
    log(f"wrote {out_path.relative_to(DATA_DIR.parent.parent)} ({out_path.stat().st_size / 1024:.1f} KB)")

    print()
    non_empty = sum(1 for i in icons_summary if i["count"] > 0)
    log(f"sanity ✓ — {non_empty}/{len(icons_summary)} icons returned data")
    for i in icons_summary[:5]:
        log(f"  · {i['label']:35s} n={i['count']:4d} top edu={i['topEducations'][:1]}")


if __name__ == "__main__":
    main()
