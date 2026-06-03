"""Download, simplify and convert the Catalonia comarques to a tiny topojson.

The source is sirisacademic/catalonia-cartography (public, MIT-friendly).
We simplify with Douglas-Peucker to ~5% of the original detail, drop
unused properties, and write the result as TopoJSON so the client only
ships ~80 KB of geometry instead of ~4 MB of GeoJSON.

Also writes a small comarques_metrics.json with one row per comarca
carrying placeholder atur / ocupació numbers tagged as such, so the
ComarcaMap can render today and be progressively swapped with real
Observatori data.
"""
from __future__ import annotations

import json

import requests
import shapely.geometry as sgeom
from topojson import Topology

from lib import CACHE_DIR, DATA_DIR, banner, log


GEO_URL = (
    "https://raw.githubusercontent.com/sirisacademic/catalonia-cartography/"
    "master/shapefiles_catalunya_comarcas.geojson"
)
GEO_LOCAL = CACHE_DIR / "geo" / "cat_comarcas.geojson"


def _fetch_geo() -> None:
    GEO_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    if GEO_LOCAL.exists() and GEO_LOCAL.stat().st_size > 100_000:
        log(f"using cached {GEO_LOCAL.relative_to(CACHE_DIR.parent)}")
        return
    log(f"downloading {GEO_URL}")
    res = requests.get(GEO_URL, timeout=60)
    res.raise_for_status()
    GEO_LOCAL.write_bytes(res.content)
    log(f"saved {GEO_LOCAL.stat().st_size / 1024:.1f} KB")


def _simplify_geom(geom_geojson: dict, tol: float) -> dict:
    shape = sgeom.shape(geom_geojson)
    simplified = shape.simplify(tol, preserve_topology=True)
    return sgeom.mapping(simplified)


def main() -> None:
    banner("09 · comarques")

    _fetch_geo()
    raw = json.loads(GEO_LOCAL.read_text())

    keep_props = {"nom_comar", "comarca", "provincia"}
    features = []
    for f in raw["features"]:
        props = {k: v for k, v in f["properties"].items() if k in keep_props}
        if "nom_comar" not in props:
            continue
        # Geometry simplification — tolerance in geographic degrees
        # ~0.003° ≈ 300 m at Catalonia's latitude, plenty for a national map
        geom = _simplify_geom(f["geometry"], tol=0.003)
        features.append({
            "type": "Feature",
            "properties": {
                "id": str(props.get("comarca", "")),
                "name": props["nom_comar"],
                "provincia": str(props.get("provincia", "")),
            },
            "geometry": geom,
        })
    log(f"{len(features)} comarca features after simplification")

    fc = {"type": "FeatureCollection", "features": features}

    # Convert to TopoJSON for compactness
    topo = Topology(fc, prequantize=False).to_dict()
    topo_path = DATA_DIR / "comarques.topo.json"
    topo_path.write_text(json.dumps(topo, ensure_ascii=False))
    log(f"wrote {topo_path.relative_to(DATA_DIR.parent.parent)} ({topo_path.stat().st_size / 1024:.1f} KB)")

    # ── comarques_metrics.json — placeholder, structured for swap-in ────
    # Generate plausible figures by provincia so the choropleth has a
    # readable gradient. Values are labelled placeholder=true.
    PROV_BASE = {
        "08": dict(atur=0.085, ocup=0.62),  # Barcelona
        "17": dict(atur=0.078, ocup=0.63),  # Girona
        "25": dict(atur=0.072, ocup=0.64),  # Lleida
        "43": dict(atur=0.110, ocup=0.58),  # Tarragona
    }
    rows = []
    for f in features:
        prov = f["properties"]["provincia"]
        base = PROV_BASE.get(prov, dict(atur=0.09, ocup=0.60))
        # Add a deterministic per-comarca offset so neighbours don't look identical
        h = sum(ord(c) for c in f["properties"]["name"]) % 13
        rows.append(
            {
                "id": f["properties"]["id"],
                "name": f["properties"]["name"],
                "provincia": prov,
                "atur_rate": round(base["atur"] + (h - 6) * 0.004, 4),
                "ocup_rate": round(base["ocup"] + (h - 6) * 0.005, 4),
                "placeholder": True,
            }
        )
    metrics_path = DATA_DIR / "comarques_metrics.json"
    metrics_path.write_text(
        json.dumps(
            {
                "source": "placeholder per provincia, to be swapped with Observatori del Treball",
                "rows": rows,
            },
            ensure_ascii=False,
            indent=None,
        )
    )
    log(f"wrote {metrics_path.relative_to(DATA_DIR.parent.parent)} ({metrics_path.stat().st_size / 1024:.1f} KB)")

    print()
    log(f"sanity ✓ — {len(features)} comarques, total atur range {min(r['atur_rate'] for r in rows):.3f}–{max(r['atur_rate'] for r in rows):.3f}")


if __name__ == "__main__":
    main()
