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
            return {
                "overlap_ratio": 0.0,
                "overlap_score": 1.0,
                "severity": "none",
                "explanation": "No overlapping plots found."
            }

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
        if overlap_ratio == 0:
            severity = "none"
        elif overlap_ratio < 0.10:
            severity = "minor"
        elif overlap_ratio < 0.30:
            severity = "moderate"
        else:
            severity = "critical"

        return {
            "overlap_ratio": round(overlap_ratio, 3),
            "overlap_score": overlap_score,
            "severity": severity,
            "explanation": (
                f"{round(overlap_ratio * 100, 2)}% of the submitted plot "
                f"overlaps with existing registered plots."
            )
        }

    except Exception as e:
        # ---------------------------------------------------------
        # 6️⃣ Fail-safe behavior
        # ---------------------------------------------------------
        return {
            "overlap_ratio": 0.0,
            "overlap_score": 0.0,
            "severity": "error",
            "explanation": f"Overlap computation failed: {str(e)}"
        }