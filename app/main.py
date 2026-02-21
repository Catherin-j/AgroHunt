# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shapely.geometry import shape
import ee

from app.schemas import PlotRequest
from app.modules.geometry import validate_geometry
from app.modules.ndvi import validate_ndvi
from app.modules.landuse import compute_land_use_score
from app.modules.crop_engine import evaluate_crop
from app.config import initialize_gee


app = FastAPI(
    title="Agricultural Plot Validation API",
    version="3.0.0"
)


# ===============================
# Initialize GEE
# ===============================
@app.on_event("startup")
def startup_event():
    initialize_gee()


# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# Root
# ===============================
@app.get("/")
def root():
    return {"message": "API running successfully"}


# ===============================
# Plot Validation
# ===============================
@app.post("/validate-plot")
def validate_plot(request: PlotRequest):

    if not request.polygon:
        raise HTTPException(status_code=400, detail="Polygon required")

    # 1️⃣ Geometry
    geometry_result = validate_geometry(request.polygon)

    if not geometry_result["valid"]:
        return {
            "decision": "FAIL",
            "stage": "geometry_validation",
            "geometry": geometry_result
        }

    # 2️⃣ NDVI
    ndvi_result = validate_ndvi(request.polygon)

    if ndvi_result.get("reason") == "No satellite images available":
        return {
            "decision": "FAIL",
            "stage": "ndvi_validation",
            "ndvi": ndvi_result
        }

    if ndvi_result["agriculture_score"] < 0.3:
        return {
            "decision": "FAIL",
            "stage": "ndvi_validation",
            "ndvi": ndvi_result
        }

    # 3️⃣ Land Use
    landuse_result = compute_land_use_score(request.polygon)

    if landuse_result["land_score"] < 0.3:
        return {
            "decision": "FAIL",
            "stage": "landuse_validation",
            "land_use": landuse_result
        }

    # 4️⃣ Crop Engine

    polygon_shape = shape(request.polygon)
    centroid = polygon_shape.centroid
    lat = centroid.y
    lon = centroid.x

    coords = list(polygon_shape.exterior.coords)
    gee_polygon = ee.Geometry.Polygon([coords])

    crop_result = evaluate_crop(
        gee_polygon,
        request.crop,
        lat,
        lon
    )

    if crop_result["crop_score"] < 0.4:
        return {
            "decision": "FAIL",
            "stage": "crop_validation",
            "crop_engine": crop_result
        }

    # ✅ FINAL PASS
    return {
        "decision": "PASS",
        "stage": "full_validation_complete",
        "geometry": geometry_result,
        "ndvi": ndvi_result,
        "land_use": landuse_result,
        "crop_engine": crop_result
    }