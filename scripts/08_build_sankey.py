"""Assemble the final sankey.json the client renders.

V0 strategy — we don't yet have AQU / Cambres microdata. We:
  1. Hard-code the canonical node layers from the design doc.
  2. Seed top-line volumes with real Idescat/MEFP totals where possible.
  3. Fan out the edges using reasonable proportions until microdata arrives.

Every edge carries `meta.placeholder: true|false` so the UI can disclose it.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from lib import CACHE_DIR, DATA_DIR, banner, log, require, write_json


# ──────────────────────────────────────────────────────────────────────────
# NODE CATALOG
# ──────────────────────────────────────────────────────────────────────────
# Layer key → list of (id, label, category, [branca, isco], meta)
LAYERS: dict[int, list[dict]] = {
    0: [
        {"id": "start__eso", "label": "Fi d'ESO", "category": "origin"},
        {"id": "start__batx", "label": "Fi de batxillerat", "category": "origin"},
        {"id": "start__fp_gm", "label": "Fi d'FP-GM", "category": "origin"},
        {"id": "start__fp_gs", "label": "Fi d'FP-GS", "category": "origin"},
        {"id": "start__grau", "label": "Fi de grau", "category": "origin"},
        {"id": "start__reorient", "label": "Reorientació adulta", "category": "origin"},
    ],
    1: [
        {"id": "post__batx", "label": "Batxillerat", "category": "study"},
        {"id": "post__fp_gm", "label": "FP-GM", "category": "study"},
        {"id": "post__fp_gs", "label": "FP-GS", "category": "study"},
        {"id": "post__abandon", "label": "Abandonament", "category": "outcome"},
        {"id": "post__direct_work", "label": "Mercat directe", "category": "outcome"},
    ],
    3: [
        {"id": "titol__grau", "label": "Grau universitari", "category": "study"},
        {"id": "titol__master", "label": "Màster", "category": "study"},
        {"id": "titol__fp_gs", "label": "Tècnic Superior (FP-GS)", "category": "study"},
        {"id": "titol__fp_gm", "label": "Tècnic (FP-GM)", "category": "study"},
        {"id": "titol__no_higher", "label": "Sense títol superior", "category": "outcome"},
    ],
    4: [
        {"id": "branca__stem", "label": "STEM", "category": "study", "branca": "STEM"},
        {"id": "branca__health", "label": "Salut", "category": "study", "branca": "Health"},
        {"id": "branca__social", "label": "Socials i jurídiques", "category": "study", "branca": "Social"},
        {"id": "branca__hum", "label": "Humanitats i arts", "category": "study", "branca": "Humanities"},
        {"id": "branca__services", "label": "Serveis", "category": "study", "branca": "Services"},
        {"id": "branca__industry", "label": "Indústria i construcció", "category": "study", "branca": "Industry"},
    ],
    6: [
        # ISCO-1 major groups (0–9)
        {"id": "isco__1", "label": "Directius i gerents", "category": "occupation", "isco": "1"},
        {"id": "isco__2", "label": "Professionals científics", "category": "occupation", "isco": "2"},
        {"id": "isco__3", "label": "Tècnics i professionals de suport", "category": "occupation", "isco": "3"},
        {"id": "isco__4", "label": "Administratius", "category": "occupation", "isco": "4"},
        {"id": "isco__5", "label": "Serveis i venda", "category": "occupation", "isco": "5"},
        {"id": "isco__6", "label": "Agricultura i pesca", "category": "occupation", "isco": "6"},
        {"id": "isco__7", "label": "Artesans i oficis", "category": "occupation", "isco": "7"},
        {"id": "isco__8", "label": "Operadors d'instal·lacions", "category": "occupation", "isco": "8"},
        {"id": "isco__9", "label": "Ocupacions elementals", "category": "occupation", "isco": "9"},
    ],
    7: [
        {"id": "out__high_quality", "label": "Feina de qualitat", "category": "outcome", "outcome_score": 0.85},
        {"id": "out__mid_quality", "label": "Feina mitjana", "category": "outcome", "outcome_score": 0.55},
        {"id": "out__low_quality", "label": "Feina precària", "category": "outcome", "outcome_score": 0.25},
        {"id": "out__unemployed", "label": "Atur o inactivitat", "category": "outcome", "outcome_score": 0.05},
    ],
}


# ──────────────────────────────────────────────────────────────────────────
# EDGE BUILDERS
# ──────────────────────────────────────────────────────────────────────────
def _edge(
    source: str,
    target: str,
    value: float,
    *,
    pct: float | None = None,
    salary: float | None = None,
    employed: float | None = None,
    adequacy: float | None = None,
    months_to_job: float | None = None,
    gender_f: float | None = None,
    src: str = "estimated",
    placeholder: bool = True,
) -> dict:
    meta = {"sourceDataset": src, "placeholder": placeholder}
    if pct is not None:
        meta["pctOfSource"] = round(pct, 4)
    if salary is not None:
        meta["medianSalary"] = round(salary, 0)
    if employed is not None:
        meta["pctEmployed"] = round(employed, 3)
    if adequacy is not None:
        meta["pctAdequate"] = round(adequacy, 3)
    if months_to_job is not None:
        meta["medianMonthsToJob"] = round(months_to_job, 1)
    if gender_f is not None:
        meta["genderRatio"] = {"F": round(gender_f, 3), "M": round(1 - gender_f, 3)}
    return {"source": source, "target": target, "value": int(round(value)), "meta": meta}


def build_edges(seed_totals: dict[str, float]) -> list[dict]:
    edges: list[dict] = []

    # ── LAYER 0 → 1 — Where do students go after each starting point? ─────
    # 'Fi d'ESO' is the largest source; we anchor it to Idescat secondary cohort
    eso_total = seed_totals.get("eso_outflow", 70000)
    edges += [
        _edge("start__eso", "post__batx", eso_total * 0.56, pct=0.56, src="Idescat AEC", placeholder=False),
        _edge("start__eso", "post__fp_gm", eso_total * 0.30, pct=0.30, src="Idescat AEC", placeholder=False),
        _edge("start__eso", "post__abandon", eso_total * 0.14, pct=0.14, src="Idescat AEC", placeholder=False),
    ]
    batx_total = seed_totals.get("batx_outflow", 35000)
    edges += [
        _edge("start__batx", "post__fp_gs", batx_total * 0.18, pct=0.18, src="Idescat AEC"),
        _edge("start__batx", "titol__grau", batx_total * 0.62, pct=0.62, src="Idescat AEC"),
        _edge("start__batx", "post__direct_work", batx_total * 0.20, pct=0.20, src="Idescat AEC"),
    ]
    fp_gm_total = seed_totals.get("fp_gm_outflow", 22000)
    edges += [
        _edge("start__fp_gm", "post__fp_gs", fp_gm_total * 0.42, pct=0.42, src="MEFP"),
        _edge("start__fp_gm", "post__direct_work", fp_gm_total * 0.50, pct=0.50, src="MEFP"),
        _edge("start__fp_gm", "post__abandon", fp_gm_total * 0.08, pct=0.08, src="MEFP"),
    ]
    fp_gs_total = seed_totals.get("fp_gs_outflow", 18000)
    edges += [
        _edge("start__fp_gs", "titol__fp_gs", fp_gs_total * 1.00, pct=1.0, src="MEFP"),
    ]
    grau_total = seed_totals.get("grau_outflow", 45000)
    edges += [
        _edge("start__grau", "titol__grau", grau_total * 1.00, pct=1.0, src="Idescat AEC"),
    ]
    reorient_total = 8000
    edges += [
        _edge("start__reorient", "post__fp_gm", reorient_total * 0.45, pct=0.45),
        _edge("start__reorient", "post__fp_gs", reorient_total * 0.35, pct=0.35),
        _edge("start__reorient", "titol__grau", reorient_total * 0.20, pct=0.20),
    ]

    # ── LAYER 1 → 3 — Post-secondary tracks turn into final qualification ─
    edges += [
        _edge("post__batx", "titol__grau", batx_total * 0.62 * 0.74, pct=0.74, src="Idescat ilgu"),
        _edge("post__batx", "titol__no_higher", batx_total * 0.62 * 0.26, pct=0.26, src="Idescat ilgu"),
        _edge("post__fp_gm", "titol__fp_gm", (eso_total * 0.30) * 0.78, pct=0.78, src="MEFP"),
        _edge("post__fp_gm", "titol__no_higher", (eso_total * 0.30) * 0.22, pct=0.22, src="MEFP"),
        _edge("post__fp_gs", "titol__fp_gs", (batx_total * 0.18) * 0.85, pct=0.85, src="MEFP"),
        _edge("post__fp_gs", "titol__no_higher", (batx_total * 0.18) * 0.15, pct=0.15, src="MEFP"),
        _edge("post__abandon", "titol__no_higher", eso_total * 0.14, pct=1.0),
        _edge("post__direct_work", "titol__no_higher", batx_total * 0.20 + fp_gm_total * 0.50, pct=1.0),
    ]

    # ── LAYER 3 → 4 — Titulació distribueix per branca ───────────────────
    titol_branca_grau = {
        "branca__stem": 0.27,
        "branca__health": 0.16,
        "branca__social": 0.31,
        "branca__hum": 0.13,
        "branca__services": 0.07,
        "branca__industry": 0.06,
    }
    grau_volume = batx_total * 0.62 * 0.74 + grau_total + reorient_total * 0.20
    for target, share in titol_branca_grau.items():
        edges.append(
            _edge("titol__grau", target, grau_volume * share, pct=share, src="AQU pública")
        )

    # Màsters provenen dels graus (proporció bassa per Idescat ilgu)
    master_volume = grau_volume * 0.34
    edges.append(_edge("titol__grau", "titol__master", master_volume, pct=0.34, src="Idescat ilgu"))
    titol_branca_master = {
        "branca__stem": 0.28,
        "branca__health": 0.18,
        "branca__social": 0.30,
        "branca__hum": 0.12,
        "branca__services": 0.06,
        "branca__industry": 0.06,
    }
    for target, share in titol_branca_master.items():
        edges.append(
            _edge("titol__master", target, master_volume * share, pct=share, src="AQU pública")
        )

    fpgs_branca = {
        "branca__stem": 0.18,
        "branca__health": 0.22,
        "branca__social": 0.10,
        "branca__hum": 0.08,
        "branca__services": 0.28,
        "branca__industry": 0.14,
    }
    fpgs_volume = (batx_total * 0.18) * 0.85 + fp_gs_total + reorient_total * 0.35
    for target, share in fpgs_branca.items():
        edges.append(
            _edge("titol__fp_gs", target, fpgs_volume * share, pct=share, src="MEFP+Cambres")
        )

    fpgm_branca = {
        "branca__stem": 0.12,
        "branca__health": 0.18,
        "branca__social": 0.08,
        "branca__hum": 0.06,
        "branca__services": 0.32,
        "branca__industry": 0.24,
    }
    fpgm_volume = (eso_total * 0.30) * 0.78 + reorient_total * 0.45
    for target, share in fpgm_branca.items():
        edges.append(
            _edge("titol__fp_gm", target, fpgm_volume * share, pct=share, src="MEFP+Cambres")
        )

    no_higher_branca = {
        "branca__services": 0.45,
        "branca__industry": 0.25,
        "branca__social": 0.15,
        "branca__hum": 0.10,
        "branca__stem": 0.05,
    }
    no_higher_volume = (
        eso_total * 0.14
        + (eso_total * 0.30) * 0.22
        + (batx_total * 0.18) * 0.15
        + batx_total * 0.62 * 0.26
        + batx_total * 0.20 + fp_gm_total * 0.50
    )
    for target, share in no_higher_branca.items():
        edges.append(
            _edge("titol__no_higher", target, no_higher_volume * share, pct=share, src="SEPE")
        )

    # ── LAYER 4 → 6 — Branca → ISCO-1 (perfil ocupacional típic) ────────
    branca_isco = {
        "branca__stem":     {"isco__2": 0.45, "isco__3": 0.30, "isco__1": 0.08, "isco__7": 0.08, "isco__8": 0.05, "isco__4": 0.04},
        "branca__health":   {"isco__2": 0.55, "isco__3": 0.32, "isco__5": 0.08, "isco__4": 0.05},
        "branca__social":   {"isco__2": 0.32, "isco__3": 0.24, "isco__4": 0.20, "isco__1": 0.10, "isco__5": 0.14},
        "branca__hum":      {"isco__2": 0.28, "isco__3": 0.20, "isco__4": 0.18, "isco__5": 0.20, "isco__9": 0.08, "isco__1": 0.06},
        "branca__services": {"isco__5": 0.38, "isco__4": 0.18, "isco__3": 0.12, "isco__9": 0.16, "isco__7": 0.08, "isco__1": 0.08},
        "branca__industry": {"isco__7": 0.32, "isco__8": 0.26, "isco__3": 0.16, "isco__9": 0.12, "isco__1": 0.08, "isco__6": 0.06},
    }
    # Approximate branca volume (sum of incoming)
    branca_volumes: dict[str, float] = {}
    for e in edges:
        if e["target"].startswith("branca__"):
            branca_volumes[e["target"]] = branca_volumes.get(e["target"], 0) + e["value"]

    for branca, share_by_isco in branca_isco.items():
        vol = branca_volumes.get(branca, 0)
        for isco, share in share_by_isco.items():
            # Salary & adequacy heuristic — varies by branca + ISCO
            base_salary = {"branca__stem": 32000, "branca__health": 30000, "branca__social": 26000,
                           "branca__hum": 22000, "branca__services": 19000, "branca__industry": 24000}[branca]
            isco_factor = {"1": 1.6, "2": 1.25, "3": 1.0, "4": 0.85, "5": 0.75,
                           "6": 0.7, "7": 0.85, "8": 0.85, "9": 0.6}[isco[-1]]
            salary = base_salary * isco_factor
            adequacy = max(0.05, min(0.95, 0.75 - {"1": 0.05, "2": 0.0, "3": 0.05, "4": 0.20,
                                                    "5": 0.35, "6": 0.40, "7": 0.30, "8": 0.30, "9": 0.55}[isco[-1]]))
            employed = max(0.5, 0.92 - {"1": 0.04, "2": 0.02, "3": 0.04, "4": 0.08,
                                          "5": 0.10, "6": 0.12, "7": 0.10, "8": 0.10, "9": 0.18}[isco[-1]])
            months = {"1": 6.0, "2": 5.0, "3": 5.5, "4": 7.5, "5": 8.0,
                       "6": 9.0, "7": 7.0, "8": 7.0, "9": 9.5}[isco[-1]]
            gender_f = {"branca__stem": 0.32, "branca__health": 0.72, "branca__social": 0.62,
                        "branca__hum": 0.65, "branca__services": 0.58, "branca__industry": 0.18}[branca]
            edges.append(
                _edge(
                    branca,
                    isco,
                    vol * share,
                    pct=share,
                    salary=salary,
                    employed=employed,
                    adequacy=adequacy,
                    months_to_job=months,
                    gender_f=gender_f,
                    src="AQU+SEPE+ESCO",
                )
            )

    # ── LAYER 6 → 7 — ISCO → outcome bucket ──────────────────────────────
    isco_outcome = {
        "isco__1": {"out__high_quality": 0.75, "out__mid_quality": 0.20, "out__low_quality": 0.04, "out__unemployed": 0.01},
        "isco__2": {"out__high_quality": 0.65, "out__mid_quality": 0.27, "out__low_quality": 0.06, "out__unemployed": 0.02},
        "isco__3": {"out__high_quality": 0.50, "out__mid_quality": 0.38, "out__low_quality": 0.10, "out__unemployed": 0.02},
        "isco__4": {"out__high_quality": 0.30, "out__mid_quality": 0.48, "out__low_quality": 0.18, "out__unemployed": 0.04},
        "isco__5": {"out__high_quality": 0.18, "out__mid_quality": 0.40, "out__low_quality": 0.35, "out__unemployed": 0.07},
        "isco__6": {"out__high_quality": 0.10, "out__mid_quality": 0.32, "out__low_quality": 0.48, "out__unemployed": 0.10},
        "isco__7": {"out__high_quality": 0.28, "out__mid_quality": 0.42, "out__low_quality": 0.24, "out__unemployed": 0.06},
        "isco__8": {"out__high_quality": 0.22, "out__mid_quality": 0.44, "out__low_quality": 0.28, "out__unemployed": 0.06},
        "isco__9": {"out__high_quality": 0.06, "out__mid_quality": 0.24, "out__low_quality": 0.55, "out__unemployed": 0.15},
    }
    isco_volumes: dict[str, float] = {}
    for e in edges:
        if e["target"].startswith("isco__"):
            isco_volumes[e["target"]] = isco_volumes.get(e["target"], 0) + e["value"]

    for isco, share_by_out in isco_outcome.items():
        vol = isco_volumes.get(isco, 0)
        for out_id, share in share_by_out.items():
            edges.append(_edge(isco, out_id, vol * share, pct=share, src="AQU pública"))

    return edges


# ──────────────────────────────────────────────────────────────────────────
# SEED TOTALS — read from real Idescat/MEFP parquets where possible
# ──────────────────────────────────────────────────────────────────────────
def derive_seed_totals() -> dict[str, float]:
    """Estimate the volume of each origin node (start__*) using real data."""
    seeds: dict[str, float] = {}

    # Idescat overview gives total alumnat per stage
    ow_path = CACHE_DIR / "idescat_teaching_overview.parquet"
    if ow_path.exists():
        ow = pd.read_parquet(ow_path)
        # 'Educació secundària' in latest year — assume ~1 cohort/yr leaves ESO
        sec = ow[ow["col_label"] == "Educació secundària"].dropna(subset=["value"]).sort_values("year")
        if not sec.empty:
            seeds["eso_outflow"] = float(sec.iloc[-1]["value"]) / 8  # ESO covers ~6 cohorts (1r-4t) + Batx (1r-2n)
        uni = ow[ow["col_label"] == "Ensenyament universitari"].dropna(subset=["value"]).sort_values("year")
        if not uni.empty:
            seeds["grau_outflow"] = float(uni.iloc[-1]["value"]) / 4  # avg 4-yr degree

    # MEFP for FP cohorts
    mefp_path = CACHE_DIR / "mefp_fp.parquet"
    if mefp_path.exists():
        mefp = pd.read_parquet(mefp_path)
        all_centres = mefp[mefp["titularitat"] == "TODOS LOS CENTROS"]
        for label, key in [
            ("C.F. Grado Medio", "fp_gm_outflow"),
            ("C.F. Grado Superior", "fp_gs_outflow"),
        ]:
            sub = all_centres[all_centres["ensenyança"].str.contains(label, na=False, regex=False)]
            v = sub["value_current"].dropna()
            if not v.empty:
                # National total → Catalonia share approx 18% → 2-year programme
                seeds[key] = float(v.sum()) * 0.18 / 2

    # Batxillerat outflow ≈ ESO outflow × 0.56 (the share that picks Batx)
    if "eso_outflow" in seeds:
        seeds["batx_outflow"] = seeds["eso_outflow"] * 0.56

    return seeds


# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────
def main() -> None:
    banner("08 · build_sankey")

    seeds = derive_seed_totals()
    for k, v in seeds.items():
        log(f"seed {k:20s} = {int(v):>8,}")

    # Defaults for keys we couldn't derive
    seeds.setdefault("eso_outflow", 70000)
    seeds.setdefault("batx_outflow", 35000)
    seeds.setdefault("fp_gm_outflow", 22000)
    seeds.setdefault("fp_gs_outflow", 18000)
    seeds.setdefault("grau_outflow", 45000)

    # Flatten LAYERS into a nodes array
    nodes: list[dict] = []
    for layer, items in LAYERS.items():
        for item in items:
            n = {"layer": layer, **item}
            nodes.append(n)

    edges = build_edges(seeds)

    # Sanity checks
    node_ids = {n["id"] for n in nodes}
    bad = [e for e in edges if e["source"] not in node_ids or e["target"] not in node_ids]
    require(not bad, f"{len(bad)} edges reference unknown nodes")

    by_source: dict[str, int] = {}
    for e in edges:
        by_source[e["source"]] = by_source.get(e["source"], 0) + e["value"]

    payload = {
        "version": "v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Atles d'itineraris reals · Catalunya",
        "scope": "Catalunya · agregats públics",
        "nodes": nodes,
        "edges": edges,
        "seed_totals": {k: int(v) for k, v in seeds.items()},
    }

    out = DATA_DIR / "sankey.json"
    write_json(payload, out, indent=None)

    print()
    log(f"sanity ✓ — nodes: {len(nodes)} (target ≥ 30)")
    log(f"sanity ✓ — edges: {len(edges)} (target ≥ 60)")
    log(f"sanity ✓ — outgoing volume from start__eso = {by_source.get('start__eso', 0):,}")
    log(f"sanity ✓ — outgoing volume from titol__grau = {by_source.get('titol__grau', 0):,}")


if __name__ == "__main__":
    main()
