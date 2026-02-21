import ee
from shapely.geometry import shape

try:
    ee.Initialize(project='agri-validation-system')
except Exception:
    ee.Authenticate()
    ee.Initialize(project='agri-validation-system')

def mask_s2_clouds(image):
    scl = image.select('SCL')
    mask = (
        scl.neq(3)  # cloud shadow
        .And(scl.neq(8))  # cloud medium prob
        .And(scl.neq(9))  # cloud high prob
        .And(scl.neq(10))  # thin cirrus
        .And(scl.neq(11))  # snow
    )
    return image.updateMask(mask)


def validate_ndvi(geojson_polygon, start_date="2023-01-01", end_date="2023-12-31"):

    result = {
        "mean_ndvi": 0,
        "vegetation_ratio": 0,
        "agriculture_score": 0,
        "reason": None
    }

    # Convert GeoJSON to GEE geometry
    polygon = shape(geojson_polygon)
    coords = list(polygon.exterior.coords)

    gee_polygon = ee.Geometry.Polygon([coords])

    # Load Sentinel-2
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(gee_polygon)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_s2_clouds)
    )

    collection_size = collection.size().getInfo()

    if collection_size == 0:
        result["reason"] = "No satellite images available"
        return result

    # Add NDVI band
    def add_ndvi(image):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)

    ndvi_collection = collection.map(add_ndvi)

    mean_ndvi = ndvi_collection.select('NDVI').mean()

    # Mean NDVI
    mean_ndvi_value = mean_ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=gee_polygon,
        scale=10,
        maxPixels=1e9
    ).getInfo()

    mean_ndvi_val = mean_ndvi_value.get("NDVI", 0)

    # Vegetation threshold
    NDVI_THRESHOLD = 0.3

    vegetation_mask = mean_ndvi.gt(NDVI_THRESHOLD).rename('veg')

    pixel_counts = vegetation_mask.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=gee_polygon,
        scale=10,
        maxPixels=1e9
    ).getInfo()

    counts = pixel_counts.get("veg", {})

    veg_pixels = counts.get("1", 0)
    non_veg_pixels = counts.get("0", 0)
    total_pixels = veg_pixels + non_veg_pixels

    vegetation_ratio = veg_pixels / total_pixels if total_pixels > 0 else 0

    # Agriculture scoring (continuous)
    agriculture_score = round(
        0.5 * min(1, mean_ndvi_val) +
        0.5 * vegetation_ratio,
        3
    )

    result.update({
        "mean_ndvi": round(mean_ndvi_val, 4),
        "vegetation_ratio": round(vegetation_ratio, 4),
        "agriculture_score": agriculture_score
    })

    return result