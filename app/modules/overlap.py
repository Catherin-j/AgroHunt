# app/modules/overlap.py

"""
MODULE 5 — Spatial Overlap Validation

Purpose:
Detect whether a newly submitted agricultural plot overlaps
with already registered plots stored in Supabase (PostGIS).

Design Goals:
- Use PostGIS for accurate spatial intersection
- Ignore self-overlap (same farmer submitting multiple times)
- Provide continuous overlap ratio
- Provide severity classification
- Fail safely if database error occurs
"""

from app.config import supabase
from shapely.geometry import shape
import geopandas as gpd


_LOCAL_PLOTS = []


def _area_m2(geom) -> float:
    gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
    gdf_metric = gdf.to_crs("EPSG:3857")
    return float(gdf_metric.area.iloc[0])


def _classify_severity(overlap_ratio: float) -> str:
    if overlap_ratio == 0:
        return "none"
    if overlap_ratio < 0.10:
        return "minor"
    if overlap_ratio < 0.30:
        return "moderate"
    return "critical"


def _try_cache_polygon(geojson_polygon: dict, farmer_id: str) -> None:
    try:
        polygon = shape(geojson_polygon)
    except Exception:
        return

    if not polygon.is_valid or polygon.is_empty:
        return

    _LOCAL_PLOTS.append({"farmer_id": farmer_id, "polygon": polygon})


def _compute_local_overlap(geojson_polygon: dict, farmer_id: str) -> dict:
    try:
        polygon = shape(geojson_polygon)
    except Exception:
        return {
            "overlap_ratio": 0.0,
            "overlap_score": 0.0,
            "severity": "error",
            "explanation": "Invalid GeoJSON for overlap check."
        }

    if not polygon.is_valid or polygon.is_empty:
        return {
            "overlap_ratio": 0.0,
            "overlap_score": 0.0,
            "severity": "error",
            "explanation": "Invalid geometry or empty polygon."
        }

    new_area = _area_m2(polygon)
    if new_area <= 0:
        return {
            "overlap_ratio": 0.0,
            "overlap_score": 0.0,
            "severity": "error",
            "explanation": "Invalid geometry or zero-area polygon."
        }

    max_overlap_area = 0.0

    for plot in _LOCAL_PLOTS:
        if plot["farmer_id"] == farmer_id:
            continue

        existing = plot["polygon"]
        if not polygon.intersects(existing):
            continue

        intersection = polygon.intersection(existing)
        if intersection.is_empty:
            continue

        max_overlap_area = max(max_overlap_area, _area_m2(intersection))

    overlap_ratio = max_overlap_area / new_area
    overlap_ratio = max(0.0, min(overlap_ratio, 1.0))
    overlap_score = round(1 - overlap_ratio, 3)
    severity = _classify_severity(overlap_ratio)

    return {
        "overlap_ratio": round(overlap_ratio, 3),
        "overlap_score": overlap_score,
        "severity": severity,
        "explanation": (
            f"{round(overlap_ratio * 100, 2)}% of the submitted plot "
            f"overlaps with existing plots (local cache)."
        )
    }


def compute_overlap_score(geojson_polygon: dict, farmer_id: str):
    """
    Computes spatial overlap ratio between new plot
    and existing plots in database.

    Parameters:
        geojson_polygon (dict): GeoJSON polygon submitted
        farmer_id (str): Unique farmer identifier

    Returns:
        dict:
            overlap_ratio (float 0–1)
            overlap_score (float 0–1)
            severity (none | minor | moderate | critical | error)
            explanation (str)
    """

    try:
        # ---------------------------------------------------------
        # 1️⃣ Call Supabase RPC (PostGIS function)
        # ---------------------------------------------------------
        response = supabase.rpc(
            "check_overlap",
            {
                "input_geojson": geojson_polygon,
                "input_farmer_id": farmer_id
            }
        ).execute()

        # ---------------------------------------------------------
        # 2️⃣ No overlaps found
        # ---------------------------------------------------------
        if not response.data:
            result = _compute_local_overlap(geojson_polygon, farmer_id)
            _try_cache_polygon(geojson_polygon, farmer_id)
            return result

        result = response.data[0]

        overlap_area = result.get("overlap_area", 0)
        new_area = result.get("new_area", 0)

        # ---------------------------------------------------------
        # 3️⃣ Safety check
        # ---------------------------------------------------------
        if not new_area or new_area == 0:
            return {
                "overlap_ratio": 0.0,
                "overlap_score": 0.0,
                "severity": "error",
                "explanation": "Invalid geometry or zero-area polygon."
            }

        # ---------------------------------------------------------
        # 4️⃣ Compute overlap ratio
        # ---------------------------------------------------------
        overlap_ratio = overlap_area / new_area
        overlap_score = round(1 - overlap_ratio, 3)

        # Clamp safety
        overlap_ratio = max(0.0, min(overlap_ratio, 1.0))
        overlap_score = max(0.0, min(overlap_score, 1.0))

        # ---------------------------------------------------------
        # 5️⃣ Severity classification
        # ---------------------------------------------------------
        severity = _classify_severity(overlap_ratio)

        result = {
            "overlap_ratio": round(overlap_ratio, 3),
            "overlap_score": overlap_score,
            "severity": severity,
            "explanation": (
                f"{round(overlap_ratio * 100, 2)}% of the submitted plot "
                f"overlaps with existing registered plots."
            )
        }

        _try_cache_polygon(geojson_polygon, farmer_id)
        return result

    except Exception as e:
        # ---------------------------------------------------------
        # 6️⃣ Fail-safe behavior
        # ---------------------------------------------------------
        result = _compute_local_overlap(geojson_polygon, farmer_id)
        if result.get("severity") == "error":
            result["explanation"] = f"Overlap computation failed: {str(e)}"

        _try_cache_polygon(geojson_polygon, farmer_id)
        return result