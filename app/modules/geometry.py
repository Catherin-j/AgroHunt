from shapely.geometry import shape
import math
import os


# -------------------------------------------------
# Lazy-Loaded World Countries Boundary
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "ne_10m_admin_0_countries.shp")

_world_gdf = None
_world_buffered = None


def _load_world_data():
    """Load world boundary data lazily on first use."""
    global _world_gdf, _world_buffered
    if _world_gdf is None:
        import geopandas as gpd

        _world_gdf = gpd.read_file(DATA_PATH)

        if _world_gdf.crs is None:
            _world_gdf.set_crs("EPSG:4326", inplace=True)

        _world_gdf = _world_gdf.to_crs("EPSG:4326")

        # Merge all landmass geometries
        world_geom = _world_gdf.geometry.unary_union

        # Small buffer (~5km) to avoid coastline precision issues
        _world_buffered = world_geom.buffer(0.05)

    return _world_gdf, _world_buffered


# -------------------------------------------------
# Region-Based Farm Size Thresholds (Research-Based)
# -------------------------------------------------

REGION_THRESHOLDS = {
    "Asia": {"large": 200, "extreme": 1000},
    "Africa": {"large": 300, "extreme": 1500},
    "Europe": {"large": 500, "extreme": 2000},
    "North America": {"large": 2000, "extreme": 5000},
    "South America": {"large": 2000, "extreme": 5000},
    "Oceania": {"large": 5000, "extreme": 10000},
    "default": {"large": 500, "extreme": 2000},
}


# -------------------------------------------------
# Geometry Validation Function
# -------------------------------------------------

def validate_geometry(geojson_polygon: dict):

    result = {
        "valid": False,
        "geometry_score": 0,
        "area_hectares": 0,
        "compactness": 0,
        "country": None,
        "continent": None,
        "reason": None
    }

    # -------------------------
    # Parse Geometry
    # -------------------------
    try:
        polygon = shape(geojson_polygon)
    except Exception:
        result["reason"] = "Invalid GeoJSON format"
        return result

    if not polygon.is_valid:
        result["reason"] = "Invalid or self-intersecting polygon"
        return result

    # -------------------------
    # Global Land Check
    # -------------------------
    world_gdf, world_buffered = _load_world_data()

    if not polygon.intersects(world_buffered):
        result["reason"] = "Polygon not located on recognized land area"
        return result

    # -------------------------
    # Identify Country & Continent
    # -------------------------
    possible_country = world_gdf[world_gdf.intersects(polygon)]

    if not possible_country.empty:
        country_row = possible_country.iloc[0]
        result["country"] = country_row["ADMIN"]
        result["continent"] = country_row["CONTINENT"]
    else:
        result["continent"] = "default"

    continent = result["continent"] or "default"
    thresholds = REGION_THRESHOLDS.get(continent, REGION_THRESHOLDS["default"])

    # -------------------------
    # Area Calculation
    # -------------------------
    import geopandas as gpd
    gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
    gdf_metric = gdf.to_crs("EPSG:3857")

    area_m2 = gdf_metric.area.iloc[0]
    area_hectares = area_m2 / 10000
    result["area_hectares"] = round(area_hectares, 2)

    # Reject extremely tiny plots
    if area_hectares < 0.05:
        result["reason"] = "Plot extremely small"
        return result

    geometry_score = 1.0

    large_threshold = thresholds["large"]
    extreme_threshold = thresholds["extreme"]

    # -------------------------
    # Progressive Area Penalty
    # -------------------------
    if area_hectares > large_threshold:

        if area_hectares >= extreme_threshold:
            geometry_score -= 0.4
            result["reason"] = "Extremely large land parcel"

        else:
            excess_ratio = area_hectares / large_threshold
            progressive_penalty = min(0.4, 0.15 * (excess_ratio - 1))
            geometry_score -= progressive_penalty
            result["reason"] = "Large commercial-scale plot"

    # -------------------------
    # Compactness Calculation
    # -------------------------
    perimeter = gdf_metric.length.iloc[0]

    if perimeter == 0:
        result["reason"] = "Invalid polygon geometry"
        return result

    compactness = (4 * math.pi * area_m2) / (perimeter ** 2)
    result["compactness"] = round(compactness, 3)

    # Progressive compactness penalty
    if compactness < 0.3:
        shape_penalty = min(0.3, (0.3 - compactness))
        geometry_score -= shape_penalty
        result["reason"] = "Irregular or elongated plot"

    geometry_score = max(0, geometry_score)

    # -------------------------
    # Finalize
    # -------------------------
    result["valid"] = True
    result["geometry_score"] = round(geometry_score, 4)

    return result