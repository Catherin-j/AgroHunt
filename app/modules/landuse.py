import ee
from datetime import datetime


def compute_land_use_score(geojson_polygon, year=None):
    """
    MODULE 3 — Land-Use Classification

    Purpose:
    Determine whether a submitted polygon represents agricultural land
    using Google Dynamic World satellite classification.

    Responsibilities of this module:
    - Classify cropland dominance
    - Handle seasonal variability (yearly majority)
    - Provide continuous confidence score
    - Ensure small polygons don't produce unstable results

    NOTE:
    Large-area validation is handled in Module 1 (Geometry Validation).
    This module does NOT reject based on area.
    """

    # ------------------------------------------------------------
    # 1️⃣ Use last complete year if not specified
    # Avoids using partial satellite data from current year
    # ------------------------------------------------------------
    if year is None:
        year = datetime.now().year - 1

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    # ------------------------------------------------------------
    # 2️⃣ Convert GeoJSON to Earth Engine geometry
    # ------------------------------------------------------------
    gee_polygon = ee.Geometry.Polygon(
        geojson_polygon["coordinates"]
    )

    # ------------------------------------------------------------
    # 3️⃣ Load Dynamic World image collection
    # Filter by:
    # - Polygon location
    # - Full year date range
    # ------------------------------------------------------------
    dw_collection = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(gee_polygon)
        .filterDate(start_date, end_date)
    )

    # Ensure dataset exists for this region/year
    collection_size = dw_collection.size().getInfo()

    if collection_size == 0:
        return {
            "crop_ratio": 0,
            "land_score": 0,
            "explanation": f"No Dynamic World data available for year {year}."
        }

    # ------------------------------------------------------------
    # 4️⃣ Compute yearly majority land class
    # This avoids seasonal misclassification issues
    # ------------------------------------------------------------
    dw_mode = dw_collection.select("label").mode()

    # Cropland class ID in Dynamic World = 4
    crop_mask = dw_mode.eq(4)

    # ------------------------------------------------------------
    # 5️⃣ Count cropland vs non-cropland pixels
    # ------------------------------------------------------------
    stats = crop_mask.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=gee_polygon,
        scale=10,          # Dynamic World resolution = 10 meters
        maxPixels=1e9
    )

    counts = stats.getInfo().get("label", {})

    crop_pixels = counts.get("1", 0)
    non_crop_pixels = counts.get("0", 0)

    total_pixels = crop_pixels + non_crop_pixels

    # ------------------------------------------------------------
    # 6️⃣ Small polygon protection
    # If too few pixels, classification becomes unstable
    # ------------------------------------------------------------
    MIN_PIXEL_THRESHOLD = 10

    if total_pixels < MIN_PIXEL_THRESHOLD:
        return {
            "crop_ratio": 0,
            "land_score": 0,
            "explanation": "Polygon too small for reliable land classification."
        }

    # ------------------------------------------------------------
    # 7️⃣ Compute cropland dominance ratio
    # ------------------------------------------------------------
    crop_ratio = crop_pixels / total_pixels

    # ------------------------------------------------------------
    # 8️⃣ Continuous scoring
    # Score directly proportional to cropland dominance
    # (More scientifically defensible than hard thresholds)
    # ------------------------------------------------------------
    land_score = round(crop_ratio, 4)

    # ------------------------------------------------------------
    # 9️⃣ Return explainable result
    # ------------------------------------------------------------
    return {
        "crop_ratio": round(crop_ratio, 3),
        "land_score": land_score,
        "explanation": (
            f"{round(crop_ratio * 100, 3)}% of area classified as cropland "
            f"(Dynamic World {year}, yearly majority). "
            f"Land score directly proportional to cropland dominance."
        )
    }