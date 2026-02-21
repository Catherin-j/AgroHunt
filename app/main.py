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
    version="4.0.0"
)

@app.on_event("startup")
def startup_event():
    initialize_gee()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API running successfully"}

@app.post("/validate-plot")
def validate_plot(request: PlotRequest):

    if not request.polygon:
        raise HTTPException(status_code=400, detail="Polygon required")

    geometry_result = validate_geometry(request.polygon)
    ndvi_result = validate_ndvi(request.polygon)
    landuse_result = compute_land_use_score(request.polygon)

    polygon_shape = shape(request.polygon)
    centroid = polygon_shape.centroid
    lat, lon = centroid.y, centroid.x

    coords = list(polygon_shape.exterior.coords)
    gee_polygon = ee.Geometry.Polygon([coords])

    crop_result = evaluate_crop(
        gee_polygon,
        request.crop,
        lat,
        lon
    )

    final_score = (
        0.20 * geometry_result["geometry_score"] +
        0.30 * ndvi_result["agriculture_score"] +
        0.25 * landuse_result["land_score"] +
        0.25 * crop_result["crop_score"]
    )

    final_score = round(final_score, 3)

    if final_score >= 0.55:
        decision = "PASS"
    elif final_score >= 0.4:
        decision = "REVIEW"
    else:
        decision = "FAIL"

    return {
        "decision": decision,
        "final_score": final_score,
        "geometry": geometry_result,
        "ndvi": ndvi_result,
        "land_use": landuse_result,
        "crop_engine": crop_result
    }