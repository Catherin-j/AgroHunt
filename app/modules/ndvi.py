# app/modules/ndvi.py

import ee
from shapely.geometry import shape


def mask_s2_clouds(image):
    scl = image.select('SCL')
    mask = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )
    return image.updateMask(mask)


def validate_ndvi(geojson_polygon, start_date="2023-01-01", end_date="2023-12-31"):

    result = {
        "mean_ndvi": 0,
        "vegetation_ratio": 0,
        "agriculture_score": 0,
        "reason": None
    }

    polygon = shape(geojson_polygon)
    coords = list(polygon.exterior.coords)
    gee_polygon = ee.Geometry.Polygon([coords])

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(gee_polygon)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
    )

    if collection.size().getInfo() == 0:
        result["reason"] = "No satellite images available"
        return result

    def add_ndvi(image):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)

    ndvi_collection = collection.map(add_ndvi)
    mean_ndvi = ndvi_collection.select('NDVI').mean()

    mean_val = mean_ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=gee_polygon,
        scale=10,
        maxPixels=1e9
    ).getInfo().get("NDVI", 0)

    NDVI_THRESHOLD = 0.25

    vegetation_mask = mean_ndvi.gt(NDVI_THRESHOLD).rename('veg')

    counts = vegetation_mask.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=gee_polygon,
        scale=10,
        maxPixels=1e9
    ).getInfo().get("veg", {})

    veg_pixels = counts.get("1", 0)
    non_veg_pixels = counts.get("0", 0)
    total = veg_pixels + non_veg_pixels

    vegetation_ratio = veg_pixels / total if total > 0 else 0

    agriculture_score = round(
        0.6 * max(0, min(1, mean_val)) +
        0.4 * vegetation_ratio,
        3
    )

    result.update({
        "mean_ndvi": round(mean_val, 4),
        "vegetation_ratio": round(vegetation_ratio, 4),
        "agriculture_score": agriculture_score
    })

    return result