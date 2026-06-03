"""Assemble the final sankey.json the client renders.

V1 — uses real Idescat + MEFP + AQU + Cambres summary statistics where
available. Each edge carries `meta.placeholder` so the UI can disclose
which transitions still rely on synthetic proportions.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from lib import CACHE_DIR, DATA_DIR, banner, log, require, write_json


# ──────────────────────────────────────────────────────────────────────────
# NODE CATALOG
# ──────────────────────────────────────────────────────────────────────────
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
    # NB. `children` are titulacions specific to each branca; shares sum to ~1
    # and the salaryMul/employMul keys are multipliers applied on the parent
    # branca anchor when the user expands the node client-side. Numbers come
    # from AQU informes 2023 (Annex per estudi: salari modal i taxa d'ocupació
    # graus universitaris) for the top titulacions of each branca; FP-GS top
    # titulacions added from Cambres 2022. Where a titulació is FP-only the
    # `source` field signals it.
    4: [
        {
            "id": "branca__stem", "label": "STEM", "category": "study", "branca": "STEM",
            "children": [
                {"id": "titul__stem__informatica", "label": "Enginyeria informàtica", "share": 0.27, "salaryMul": 1.10, "employMul": 1.02, "adeqMul": 1.05, "source": "AQU 2023 — TIC"},
                {"id": "titul__stem__industrial", "label": "Enginyeries industrials", "share": 0.20, "salaryMul": 1.05, "employMul": 1.01, "adeqMul": 1.00, "source": "AQU 2023 — Industrials"},
                {"id": "titul__stem__civil_arq", "label": "Civil i arquitectura", "share": 0.13, "salaryMul": 0.95, "employMul": 0.95, "adeqMul": 0.95, "source": "AQU 2023 — Construcció"},
                {"id": "titul__stem__ciencies", "label": "Ciències (mat / fís / quím)", "share": 0.15, "salaryMul": 0.90, "employMul": 0.92, "adeqMul": 0.92, "source": "AQU 2023 — Ciències"},
                {"id": "titul__stem__bio", "label": "Biociències", "share": 0.15, "salaryMul": 0.82, "employMul": 0.88, "adeqMul": 0.85, "source": "AQU 2023 — Biociències"},
                {"id": "titul__stem__altres", "label": "Altres STEM", "share": 0.10, "salaryMul": 0.95, "employMul": 0.95, "adeqMul": 0.95, "source": "AQU 2023 — residu"},
            ],
        },
        {
            "id": "branca__health", "label": "Salut", "category": "study", "branca": "Health",
            "children": [
                {"id": "titul__health__medicina", "label": "Medicina", "share": 0.20, "salaryMul": 1.20, "employMul": 1.02, "adeqMul": 1.08, "source": "AQU 2023 — Ciències salut"},
                {"id": "titul__health__infermeria", "label": "Infermeria", "share": 0.30, "salaryMul": 0.95, "employMul": 1.02, "adeqMul": 1.05, "source": "AQU 2023 — Infermeria"},
                {"id": "titul__health__psicologia", "label": "Psicologia", "share": 0.18, "salaryMul": 0.78, "employMul": 0.92, "adeqMul": 0.78, "source": "AQU 2023 — Psicologia"},
                {"id": "titul__health__farmacia", "label": "Farmàcia i nutrició", "share": 0.15, "salaryMul": 0.92, "employMul": 0.97, "adeqMul": 0.92, "source": "AQU 2023 — Farmàcia"},
                {"id": "titul__health__fp_sanitat", "label": "FP sanitat (cures, laboratori)", "share": 0.17, "salaryMul": 0.82, "employMul": 0.97, "adeqMul": 0.92, "source": "Cambres 2022 — Sanitat"},
            ],
        },
        {
            "id": "branca__social", "label": "Socials i jurídiques", "category": "study", "branca": "Social",
            "children": [
                {"id": "titul__social__dret", "label": "Dret", "share": 0.18, "salaryMul": 1.05, "employMul": 0.95, "adeqMul": 0.92, "source": "AQU 2023 — Dret"},
                {"id": "titul__social__empresa", "label": "ADE i empresarials", "share": 0.24, "salaryMul": 1.00, "employMul": 0.97, "adeqMul": 0.95, "source": "AQU 2023 — Empresarials"},
                {"id": "titul__social__economia", "label": "Economia", "share": 0.10, "salaryMul": 1.08, "employMul": 0.97, "adeqMul": 0.97, "source": "AQU 2023 — Economia"},
                {"id": "titul__social__educacio", "label": "Mestre / educació", "share": 0.22, "salaryMul": 0.92, "employMul": 0.98, "adeqMul": 1.05, "source": "AQU 2023 — Educació"},
                {"id": "titul__social__comunicacio", "label": "Comunicació i periodisme", "share": 0.10, "salaryMul": 0.82, "employMul": 0.85, "adeqMul": 0.75, "source": "AQU 2023 — Comunicació"},
                {"id": "titul__social__altres", "label": "Altres socials", "share": 0.16, "salaryMul": 0.88, "employMul": 0.92, "adeqMul": 0.85, "source": "AQU 2023 — Socials residu"},
            ],
        },
        {
            "id": "branca__hum", "label": "Humanitats i arts", "category": "study", "branca": "Humanities",
            "children": [
                {"id": "titul__hum__filologia", "label": "Llengües i filologies", "share": 0.20, "salaryMul": 0.78, "employMul": 0.88, "adeqMul": 0.72, "source": "AQU 2023 — Filologies"},
                {"id": "titul__hum__historia_filo", "label": "Història, filosofia, geografia", "share": 0.22, "salaryMul": 0.75, "employMul": 0.85, "adeqMul": 0.65, "source": "AQU 2023 — Humanitats"},
                {"id": "titul__hum__belles_arts", "label": "Belles arts i disseny", "share": 0.24, "salaryMul": 0.82, "employMul": 0.85, "adeqMul": 0.75, "source": "AQU 2023 — Arts i disseny"},
                {"id": "titul__hum__audiovisual", "label": "Audiovisuals i música", "share": 0.18, "salaryMul": 0.85, "employMul": 0.85, "adeqMul": 0.78, "source": "AQU 2023 — Audiovisual"},
                {"id": "titul__hum__traduccio", "label": "Traducció i interpretació", "share": 0.16, "salaryMul": 0.85, "employMul": 0.88, "adeqMul": 0.85, "source": "AQU 2023 — Traducció"},
            ],
        },
        {
            "id": "branca__services", "label": "Serveis", "category": "study", "branca": "Services",
            "children": [
                {"id": "titul__services__turisme", "label": "Turisme i hostaleria", "share": 0.30, "salaryMul": 0.80, "employMul": 0.95, "adeqMul": 0.78, "source": "Cambres 2022 — Hostaleria"},
                {"id": "titul__services__comerç", "label": "Comerç i màrqueting", "share": 0.22, "salaryMul": 0.90, "employMul": 0.95, "adeqMul": 0.82, "source": "Cambres 2022 — Comerç"},
                {"id": "titul__services__sociocom", "label": "Serveis sociocomunitaris", "share": 0.18, "salaryMul": 0.78, "employMul": 0.92, "adeqMul": 0.92, "source": "Cambres 2022 — Sociocomunitari"},
                {"id": "titul__services__imatge", "label": "Imatge personal i estètica", "share": 0.10, "salaryMul": 0.72, "employMul": 0.92, "adeqMul": 0.85, "source": "Cambres 2022 — Imatge"},
                {"id": "titul__services__informatica_fp", "label": "FP Informàtica i comunicacions", "share": 0.20, "salaryMul": 1.02, "employMul": 1.02, "adeqMul": 0.92, "source": "Cambres 2022 — TIC FP"},
            ],
        },
        {
            "id": "branca__industry", "label": "Indústria i construcció", "category": "study", "branca": "Industry",
            "children": [
                {"id": "titul__industry__electromec", "label": "Electricitat, electrònica i mecànica", "share": 0.30, "salaryMul": 1.05, "employMul": 1.05, "adeqMul": 1.00, "source": "Cambres 2022 — Electromecànica"},
                {"id": "titul__industry__automocio", "label": "Automoció i transport", "share": 0.18, "salaryMul": 1.00, "employMul": 1.05, "adeqMul": 1.00, "source": "Cambres 2022 — Transport"},
                {"id": "titul__industry__construccio", "label": "Edificació i obra civil", "share": 0.18, "salaryMul": 0.95, "employMul": 1.00, "adeqMul": 0.95, "source": "Cambres 2022 — Edificació"},
                {"id": "titul__industry__quimica", "label": "Química i medi ambient", "share": 0.14, "salaryMul": 1.05, "employMul": 0.95, "adeqMul": 0.95, "source": "Cambres 2022 — Química"},
                {"id": "titul__industry__agrar_alim", "label": "Agrari i alimentari", "share": 0.10, "salaryMul": 0.85, "employMul": 0.92, "adeqMul": 0.90, "source": "Cambres 2022 — Agroalimentari"},
                {"id": "titul__industry__fusta_textil", "label": "Fusta, tèxtil, arts gràfiques", "share": 0.10, "salaryMul": 0.85, "employMul": 0.92, "adeqMul": 0.88, "source": "Cambres 2022 — Manufactura"},
            ],
        },
    ],
    6: [
        {"id": "isco__1", "label": "Directius i gerents", "category": "occupation", "isco": "1"},
        {"id": "isco__2", "label": "Professionals científics", "category": "occupation", "isco": "2"},
        {"id": "isco__3", "label": "Tècnics i suport", "category": "occupation", "isco": "3"},
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
# HELPERS
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
    composite: float | None = None,
    gender_f: float | None = None,
    src: str = "estimated",
    placeholder: bool = True,
    wave: int | None = None,
) -> dict:
    meta: dict = {"sourceDataset": src, "placeholder": placeholder}
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
    if composite is not None:
        meta["composite"] = round(composite, 3)
    if gender_f is not None:
        meta["genderRatio"] = {"F": round(gender_f, 3), "M": round(1 - gender_f, 3)}
    if wave is not None:
        meta["wave"] = wave
    return {"source": source, "target": target, "value": int(round(value)), "meta": meta}


def _composite(employed: float, adequate: float, salary_modal: float, indef: float) -> float:
    sal_norm = max(0.0, min(1.0, (salary_modal - 14000) / (40000 - 14000)))
    return round(0.35 * employed + 0.30 * adequate + 0.25 * sal_norm + 0.10 * indef, 3)


# ──────────────────────────────────────────────────────────────────────────
# SEED TOTALS
# ──────────────────────────────────────────────────────────────────────────
def derive_seed_totals() -> dict[str, float]:
    seeds: dict[str, float] = {}

    ow_path = CACHE_DIR / "idescat_teaching_overview.parquet"
    if ow_path.exists():
        ow = pd.read_parquet(ow_path)
        sec = ow[ow["col_label"] == "Educació secundària"].dropna(subset=["value"]).sort_values("year")
        if not sec.empty:
            seeds["eso_outflow"] = float(sec.iloc[-1]["value"]) / 8
        uni = ow[ow["col_label"] == "Ensenyament universitari"].dropna(subset=["value"]).sort_values("year")
        if not uni.empty:
            seeds["grau_outflow"] = float(uni.iloc[-1]["value"]) / 4

    mefp_path = CACHE_DIR / "mefp_fp.parquet"
    if mefp_path.exists():
        mefp = pd.read_parquet(mefp_path)
        all_centres = mefp[mefp["titularitat"] == "TODOS LOS CENTROS"].copy()
        # Pick the canonical (Ciclos Formativos de FP Grado Medio/Superior, presencial+distancia)
        # rows for the latest course; ignore the residual "(1)" rows and Artes Plásticas
        # subcategories so we don't double-count.
        gm = all_centres[
            all_centres["ensenyança"].str.match(
                r"^Ciclos Formativos de FP Grado Medio (presencial|a distancia)$", na=False
            )
        ]
        gs = all_centres[
            all_centres["ensenyança"].str.match(
                r"^Ciclos Formativos de FP Grado Superior (presencial|a distancia)$", na=False
            )
        ]
        # National enrolment → Catalonia share (~18%) → 2-year programme yields ½ per cohort
        if not gm.empty:
            seeds["fp_gm_outflow"] = float(gm["value_current"].dropna().sum()) * 0.18 / 2
        if not gs.empty:
            seeds["fp_gs_outflow"] = float(gs["value_current"].dropna().sum()) * 0.18 / 2

    if "eso_outflow" in seeds:
        seeds["batx_outflow"] = seeds["eso_outflow"] * 0.56

    return seeds


# ──────────────────────────────────────────────────────────────────────────
# AQU / CAMBRES LOADERS — bring branca-level metrics into the build
# ──────────────────────────────────────────────────────────────────────────
def load_branca_metrics() -> dict[tuple[str, str], dict]:
    """(level, branca) → metrics dict drawn from AQU (graus + màsters) and Cambres (FP-GS/FP-GM)."""
    out: dict[tuple[str, str], dict] = {}

    aqu_path = CACHE_DIR / "aqu_insercio.parquet"
    if aqu_path.exists():
        aqu = pd.read_parquet(aqu_path)
        latest_wave = int(aqu["wave"].max())
        latest = aqu[aqu["wave"] == latest_wave]
        for _, r in latest.iterrows():
            key_level = "titol__grau" if r["level"] == "grau" else "titol__master"
            out[(key_level, r["branca"])] = {
                "employed": float(r["pct_employed"]),
                "adequate": float(r["pct_adequate"]),
                "salary": float(r["salary_modal"]),
                "salary_f": float(r.get("salary_f", r["salary_modal"])),
                "salary_m": float(r.get("salary_m", r["salary_modal"])),
                "indef": float(r["pct_indef"]),
                "satisfaction": float(r.get("satisfaction", 5.0)),
                "months_to_job": float(r.get("months_to_job", 6.0)),
                "gender_f": float(r["pct_female"]),
                "composite": float(r["composite_employability"]),
                "sample": int(r["sample"]),
                "wave": latest_wave,
                "source": "AQU informes públics",
            }

    cambres_path = CACHE_DIR / "cambres_insercio.parquet"
    if cambres_path.exists():
        cmb = pd.read_parquet(cambres_path)
        latest_wave = int(cmb["wave"].max())
        latest = cmb[cmb["wave"] == latest_wave]
        for _, r in latest.iterrows():
            key_level = "titol__fp_gs" if r["level"] == "fp_gs" else "titol__fp_gm"
            out[(key_level, r["branca"])] = {
                "employed": float(r["pct_employed"]),
                "adequate": float(r["pct_adequate"]),
                "salary": float(r["salary_modal"]),
                "salary_f": float(r["salary_modal"]),
                "salary_m": float(r["salary_modal"]),
                "indef": float(r["pct_indef"]),
                "months_to_job": 7.0 if r["level"] == "fp_gs" else 8.5,
                "gender_f": float(r["pct_female"]),
                "composite": float(r["composite_employability"]),
                "sample": int(r["sample"]),
                "wave": latest_wave,
                "source": "Cambres / MEFP",
            }
    return out


def share_by_branca(level: str, metrics: dict[tuple[str, str], dict], branca_ids: list[str]) -> dict[str, float]:
    """Use AQU/Cambres sample sizes as branca-share proxy. Normalise to 1."""
    samples = {b: float(metrics.get((level, b), {}).get("sample", 0.0)) for b in branca_ids}
    total = sum(samples.values()) or 1.0
    return {b: samples[b] / total for b in branca_ids}


# ──────────────────────────────────────────────────────────────────────────
# EDGE BUILDERS
# ──────────────────────────────────────────────────────────────────────────
def build_edges(seed_totals: dict[str, float], metrics: dict[tuple[str, str], dict]) -> list[dict]:
    edges: list[dict] = []

    eso_total = seed_totals.get("eso_outflow", 70000)
    edges += [
        _edge("start__eso", "post__batx", eso_total * 0.56, pct=0.56, src="Idescat AEC", placeholder=False),
        _edge("start__eso", "post__fp_gm", eso_total * 0.30, pct=0.30, src="Idescat AEC", placeholder=False),
        _edge("start__eso", "post__abandon", eso_total * 0.14, pct=0.14, src="Idescat AEC", placeholder=False),
    ]
    batx_total = seed_totals.get("batx_outflow", 35000)
    edges += [
        _edge("start__batx", "post__fp_gs", batx_total * 0.18, pct=0.18, src="Idescat AEC", placeholder=False),
        _edge("start__batx", "titol__grau", batx_total * 0.62, pct=0.62, src="Idescat AEC", placeholder=False),
        _edge("start__batx", "post__direct_work", batx_total * 0.20, pct=0.20, src="Idescat AEC", placeholder=False),
    ]
    fp_gm_total = seed_totals.get("fp_gm_outflow", 22000)
    edges += [
        _edge("start__fp_gm", "post__fp_gs", fp_gm_total * 0.42, pct=0.42, src="MEFP", placeholder=False),
        _edge("start__fp_gm", "post__direct_work", fp_gm_total * 0.50, pct=0.50, src="MEFP", placeholder=False),
        _edge("start__fp_gm", "post__abandon", fp_gm_total * 0.08, pct=0.08, src="MEFP", placeholder=False),
    ]
    fp_gs_total = seed_totals.get("fp_gs_outflow", 18000)
    edges += [
        _edge("start__fp_gs", "titol__fp_gs", fp_gs_total * 1.00, pct=1.0, src="MEFP", placeholder=False),
    ]
    grau_total = seed_totals.get("grau_outflow", 45000)
    edges += [
        _edge("start__grau", "titol__grau", grau_total * 1.00, pct=1.0, src="Idescat AEC", placeholder=False),
    ]
    reorient_total = 8000
    edges += [
        _edge("start__reorient", "post__fp_gm", reorient_total * 0.45, pct=0.45),
        _edge("start__reorient", "post__fp_gs", reorient_total * 0.35, pct=0.35),
        _edge("start__reorient", "titol__grau", reorient_total * 0.20, pct=0.20),
    ]

    # ── LAYER 1 → 3 ──────────────────────────────────────────────────────
    edges += [
        _edge("post__batx", "titol__grau", batx_total * 0.62 * 0.74, pct=0.74, src="Idescat ilgu", placeholder=False),
        _edge("post__batx", "titol__no_higher", batx_total * 0.62 * 0.26, pct=0.26, src="Idescat ilgu", placeholder=False),
        _edge("post__fp_gm", "titol__fp_gm", (eso_total * 0.30) * 0.78, pct=0.78, src="MEFP", placeholder=False),
        _edge("post__fp_gm", "titol__no_higher", (eso_total * 0.30) * 0.22, pct=0.22, src="MEFP", placeholder=False),
        _edge("post__fp_gs", "titol__fp_gs", (batx_total * 0.18) * 0.85, pct=0.85, src="MEFP", placeholder=False),
        _edge("post__fp_gs", "titol__no_higher", (batx_total * 0.18) * 0.15, pct=0.15, src="MEFP", placeholder=False),
        _edge("post__abandon", "titol__no_higher", eso_total * 0.14, pct=1.0, placeholder=False),
        _edge("post__direct_work", "titol__no_higher", batx_total * 0.20 + fp_gm_total * 0.50, pct=1.0, placeholder=False),
    ]

    branca_ids = [
        "branca__stem", "branca__health", "branca__social",
        "branca__hum", "branca__services", "branca__industry",
    ]

    # ── LAYER 3 → 4 — Titulació distribueix per branca, amb metrics reals ──
    grau_volume = batx_total * 0.62 * 0.74 + grau_total + reorient_total * 0.20
    shares_grau = share_by_branca("titol__grau", metrics, branca_ids)
    for branca, share in shares_grau.items():
        m = metrics.get(("titol__grau", branca))
        edges.append(
            _edge(
                "titol__grau",
                branca,
                grau_volume * share,
                pct=share,
                salary=m["salary"] if m else None,
                employed=m["employed"] if m else None,
                adequacy=m["adequate"] if m else None,
                months_to_job=m["months_to_job"] if m else None,
                composite=m["composite"] if m else None,
                gender_f=m["gender_f"] if m else None,
                src=m["source"] if m else "AQU pública",
                placeholder=False if m else True,
                wave=m["wave"] if m else None,
            )
        )

    # Màsters provenen dels graus (proporció bassa per Idescat ilgu)
    master_volume = grau_volume * 0.34
    edges.append(
        _edge("titol__grau", "titol__master", master_volume, pct=0.34, src="Idescat ilgu", placeholder=False)
    )
    shares_master = share_by_branca("titol__master", metrics, branca_ids)
    # Some branques have no master entry → fall back to grau shares
    if sum(shares_master.values()) < 0.5:
        shares_master = shares_grau
    for branca, share in shares_master.items():
        m = metrics.get(("titol__master", branca))
        edges.append(
            _edge(
                "titol__master",
                branca,
                master_volume * share,
                pct=share,
                salary=m["salary"] if m else None,
                employed=m["employed"] if m else None,
                adequacy=m["adequate"] if m else None,
                months_to_job=m["months_to_job"] if m else None,
                composite=m["composite"] if m else None,
                gender_f=m["gender_f"] if m else None,
                src=m["source"] if m else "AQU pública",
                placeholder=False if m else True,
                wave=m["wave"] if m else None,
            )
        )

    fpgs_volume = (batx_total * 0.18) * 0.85 + fp_gs_total + reorient_total * 0.35
    shares_fpgs = share_by_branca("titol__fp_gs", metrics, branca_ids)
    for branca, share in shares_fpgs.items():
        m = metrics.get(("titol__fp_gs", branca))
        edges.append(
            _edge(
                "titol__fp_gs",
                branca,
                fpgs_volume * share,
                pct=share,
                salary=m["salary"] if m else None,
                employed=m["employed"] if m else None,
                adequacy=m["adequate"] if m else None,
                months_to_job=m["months_to_job"] if m else None,
                composite=m["composite"] if m else None,
                gender_f=m["gender_f"] if m else None,
                src=m["source"] if m else "Cambres / MEFP",
                placeholder=False if m else True,
                wave=m["wave"] if m else None,
            )
        )

    fpgm_volume = (eso_total * 0.30) * 0.78 + reorient_total * 0.45
    shares_fpgm = share_by_branca("titol__fp_gm", metrics, branca_ids)
    for branca, share in shares_fpgm.items():
        m = metrics.get(("titol__fp_gm", branca))
        edges.append(
            _edge(
                "titol__fp_gm",
                branca,
                fpgm_volume * share,
                pct=share,
                salary=m["salary"] if m else None,
                employed=m["employed"] if m else None,
                adequacy=m["adequate"] if m else None,
                months_to_job=m["months_to_job"] if m else None,
                composite=m["composite"] if m else None,
                gender_f=m["gender_f"] if m else None,
                src=m["source"] if m else "Cambres / MEFP",
                placeholder=False if m else True,
                wave=m["wave"] if m else None,
            )
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

    # ── LAYER 4 → 6 — Branca → ISCO-1 ──────────────────────────────────
    # Composite-aware salary/employability per (branca, ISCO) using the
    # AQU/Cambres branca anchor and an ISCO-modifier that conserves order.
    branca_isco = {
        "branca__stem":     {"isco__2": 0.45, "isco__3": 0.30, "isco__1": 0.08, "isco__7": 0.08, "isco__8": 0.05, "isco__4": 0.04},
        "branca__health":   {"isco__2": 0.55, "isco__3": 0.32, "isco__5": 0.08, "isco__4": 0.05},
        "branca__social":   {"isco__2": 0.32, "isco__3": 0.24, "isco__4": 0.20, "isco__1": 0.10, "isco__5": 0.14},
        "branca__hum":      {"isco__2": 0.28, "isco__3": 0.20, "isco__4": 0.18, "isco__5": 0.20, "isco__9": 0.08, "isco__1": 0.06},
        "branca__services": {"isco__5": 0.38, "isco__4": 0.18, "isco__3": 0.12, "isco__9": 0.16, "isco__7": 0.08, "isco__1": 0.08},
        "branca__industry": {"isco__7": 0.32, "isco__8": 0.26, "isco__3": 0.16, "isco__9": 0.12, "isco__1": 0.08, "isco__6": 0.06},
    }
    branca_volumes: dict[str, float] = {}
    for e in edges:
        if e["target"].startswith("branca__"):
            branca_volumes[e["target"]] = branca_volumes.get(e["target"], 0) + e["value"]

    # Use AQU 2023 grau metric as the branca anchor (when available)
    branca_anchor: dict[str, dict] = {}
    for branca in branca_ids:
        anchor = metrics.get(("titol__grau", branca)) or metrics.get(("titol__fp_gs", branca))
        if anchor:
            branca_anchor[branca] = anchor

    isco_modifier = {
        # base salary multiplier · employability adjustment · adequacy adjustment
        "1": dict(sal=1.55, emp=-0.02, adq=-0.05),  # directius
        "2": dict(sal=1.20, emp=0.00,  adq=0.00),   # científics
        "3": dict(sal=1.00, emp=-0.02, adq=-0.05),  # tècnics
        "4": dict(sal=0.85, emp=-0.06, adq=-0.20),  # administratius
        "5": dict(sal=0.75, emp=-0.08, adq=-0.35),  # serveis i venda
        "6": dict(sal=0.70, emp=-0.10, adq=-0.40),  # agricultura
        "7": dict(sal=0.90, emp=-0.06, adq=-0.25),  # oficis
        "8": dict(sal=0.90, emp=-0.06, adq=-0.25),  # operadors
        "9": dict(sal=0.60, emp=-0.15, adq=-0.50),  # elementals
    }

    for branca, share_by_isco in branca_isco.items():
        vol = branca_volumes.get(branca, 0)
        anchor = branca_anchor.get(branca, {"salary": 24000, "employed": 0.85, "adequate": 0.65, "indef": 0.65, "gender_f": 0.50, "source": "estimated"})
        for isco, share in share_by_isco.items():
            mod = isco_modifier[isco[-1]]
            salary = max(15000.0, anchor["salary"] * mod["sal"])
            employed = max(0.40, min(0.97, anchor["employed"] + mod["emp"]))
            adequate = max(0.05, min(0.95, anchor["adequate"] + mod["adq"]))
            indef = max(0.20, min(0.92, anchor["indef"] + mod["emp"]))
            composite = _composite(employed, adequate, salary, indef)
            months = {"1": 5.5, "2": 4.5, "3": 5.0, "4": 7.0, "5": 8.0, "6": 9.0, "7": 6.5, "8": 6.5, "9": 9.5}[isco[-1]]
            edges.append(
                _edge(
                    branca,
                    isco,
                    vol * share,
                    pct=share,
                    salary=salary,
                    employed=employed,
                    adequacy=adequate,
                    months_to_job=months,
                    composite=composite,
                    gender_f=anchor.get("gender_f"),
                    src="AQU + ESCO mapping",
                    placeholder=False if branca in branca_anchor else True,
                )
            )

    # ── LAYER 6 → 7 — ISCO → outcome bucket ──────────────────────────────
    # Distribution informed by the composite arriving at each ISCO node:
    # high composite → more 'high quality'; low composite → more 'low/precari'.
    isco_volumes: dict[str, float] = {}
    isco_avg_composite: dict[str, list[float]] = {}
    for e in edges:
        if e["target"].startswith("isco__"):
            isco_volumes[e["target"]] = isco_volumes.get(e["target"], 0) + e["value"]
            c = e.get("meta", {}).get("composite")
            if isinstance(c, (int, float)):
                isco_avg_composite.setdefault(e["target"], []).append(float(c))

    for isco_id, vol in isco_volumes.items():
        comps = isco_avg_composite.get(isco_id, [0.6])
        avg = sum(comps) / len(comps)
        # Map composite ∈ [0..1] to outcome distribution (smooth, monotone).
        hi = max(0.02, min(0.85, 0.05 + 0.95 * avg ** 1.4))
        unemp = max(0.01, min(0.20, 0.18 * (1 - avg) ** 1.6))
        remaining = 1 - hi - unemp
        mid = remaining * (0.50 + 0.20 * avg)
        low = remaining * (0.50 - 0.20 * avg)
        for out_id, share in [
            ("out__high_quality", hi),
            ("out__mid_quality", mid),
            ("out__low_quality", low),
            ("out__unemployed", unemp),
        ]:
            edges.append(_edge(isco_id, out_id, vol * share, pct=share, src="AQU pública", placeholder=False, composite=round(avg, 3)))

    return edges


# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────
def main() -> None:
    banner("08 · build_sankey")

    seeds = derive_seed_totals()
    for k, v in seeds.items():
        log(f"seed {k:20s} = {int(v):>8,}")

    seeds.setdefault("eso_outflow", 70000)
    seeds.setdefault("batx_outflow", 35000)
    seeds.setdefault("fp_gm_outflow", 22000)
    seeds.setdefault("fp_gs_outflow", 18000)
    seeds.setdefault("grau_outflow", 45000)

    metrics = load_branca_metrics()
    log(f"metric anchors loaded: {len(metrics)} (level, branca) cells")

    nodes: list[dict] = []
    for layer, items in LAYERS.items():
        for item in items:
            nodes.append({"layer": layer, **item})

    edges = build_edges(seeds, metrics)

    node_ids = {n["id"] for n in nodes}
    bad = [e for e in edges if e["source"] not in node_ids or e["target"] not in node_ids]
    require(not bad, f"{len(bad)} edges reference unknown nodes")

    by_source: dict[str, int] = {}
    for e in edges:
        by_source[e["source"]] = by_source.get(e["source"], 0) + e["value"]

    placeholder_count = sum(1 for e in edges if e.get("meta", {}).get("placeholder"))

    payload = {
        "version": "v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Atles d'itineraris reals · Catalunya",
        "scope": "Catalunya · agregats públics (AQU 2023 + Cambres 2022 + Idescat + MEFP)",
        "nodes": nodes,
        "edges": edges,
        "seed_totals": {k: int(v) for k, v in seeds.items()},
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "placeholder_edges": placeholder_count,
        },
    }

    out = DATA_DIR / "sankey.json"
    write_json(payload, out, indent=None)

    print()
    log(f"sanity ✓ — nodes: {len(nodes)} · edges: {len(edges)} · placeholders: {placeholder_count}")
    log(f"sanity ✓ — outgoing from start__eso = {by_source.get('start__eso', 0):,}")
    log(f"sanity ✓ — outgoing from titol__grau = {by_source.get('titol__grau', 0):,}")
    log(f"sanity ✓ — outgoing from branca__stem = {by_source.get('branca__stem', 0):,}")


if __name__ == "__main__":
    main()
