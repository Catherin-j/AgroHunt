# app/modules/overlap.py

"""
MODULE 5 — Spatial Overlap Validation (PostGIS Version)

Purpose:
Detect whether a newly submitted agricultural plot overlaps
with already registered plots stored in Supabase (PostGIS).

Design:
- Uses raw SQL with psycopg2
- Uses ST_Intersects + ST_Intersection
- Ignores plots from same farmer
- Computes continuous overlap ratio
- Provides severity classification
- Safe error handling
"""

import json
from app.database.connection import get_connection, return_connection


def compute_overlap_score(geojson_polygon: dict, farmer_id: str):
    """
    Computes spatial overlap ratio between new plot
    and existing plots in database.

    Returns:
        overlap_ratio (0–1)
        overlap_score (0–1)
        severity (none | minor | moderate | fraud_risk | critical | error)
        explanation (str)
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # ---------------------------------------------------------
        # 1️⃣ Convert GeoJSON to PostGIS geometry
        # ---------------------------------------------------------
        geojson_str = json.dumps(geojson_polygon)

        # ---------------------------------------------------------
        # 2️⃣ SQL: Compute overlap area
        # ---------------------------------------------------------
        query = """
        WITH new_plot AS (
            SELECT ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326) AS geom
        )
        SELECT
            COALESCE(
                SUM(
                    ST_Area(
                        ST_Intersection(p.geom::geography, n.geom::geography)
                    )
                ),
                0
            ) AS overlap_area,

            MAX(ST_Area(n.geom::geography)) AS new_area

        FROM new_plot n
        LEFT JOIN plots p
            ON ST_Intersects(p.geom, n.geom)
           AND p.farmer_id <> %s;
        """

        cur.execute(query, (geojson_str, farmer_id))
        result = cur.fetchone()

        # ---------------------------------------------------------
        # Null-check on query result
        # ---------------------------------------------------------
        if result is None:
            return {
                "overlap_ratio": 0.0,
                "overlap_score": 0.0,
                "severity": "error",
                "explanation": "Overlap query returned no results."
            }

        overlap_area = result[0] or 0
        new_area = result[1] or 0

        # ---------------------------------------------------------
        # 3️⃣ Safety check
        # ---------------------------------------------------------
        if new_area == 0:
            return {
                "overlap_ratio": 0.0,
                "overlap_score": 0.0,
                "severity": "error",
                "explanation": "Invalid geometry or zero-area polygon."
            }

        # ---------------------------------------------------------
        # 4️⃣ Compute ratio
        # ---------------------------------------------------------
        overlap_ratio = overlap_area / new_area
        overlap_ratio = max(0.0, min(overlap_ratio, 1.0))

        overlap_score = round(1 - overlap_ratio, 3)

        # ---------------------------------------------------------
        # 5️⃣ Severity classification
        # ---------------------------------------------------------
        if overlap_ratio == 0:
            severity = "none"
        elif overlap_ratio < 0.10:
            severity = "minor"
        elif overlap_ratio < 0.30:
            severity = "moderate"
        elif overlap_ratio < 0.50:
            severity = "fraud_risk"
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
        return {
            "overlap_ratio": 0.0,
            "overlap_score": 0.0,
            "severity": "error",
            "explanation": f"Overlap computation failed: {str(e)}"
        }

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            return_connection(conn)