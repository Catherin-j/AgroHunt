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
from app.modules.overlap import compute_overlap_score
from app.modules.explainability import generate_explainability
from app.config import initialize_gee

#cath
from app.modules.scoring_engine import ScoringEngine
from app.config import SCORING_WEIGHTS, PASS_THRESHOLD
#cath


app = FastAPI(
    title="Agricultural Plot Validation API",
    version="5.0.0"
)


# ===============================
# Initialize Google Earth Engine
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
    return {"message": "Agricultural Plot Validation API v5.0 running"}


# ===============================
# Plot Validation Endpoint
# ===============================
@app.post("/validate-plot")
def validate_plot(request: PlotRequest):

    if not request.polygon:
        raise HTTPException(status_code=400, detail="Polygon required")

    # -------------------------------------------------
    # 1️⃣ Geometry Validation
    # -------------------------------------------------
    geometry_result = validate_geometry(request.polygon)

    if not geometry_result["valid"]:
        return {
            "decision": "FAIL",
            "reason": "Invalid geometry",
            "geometry": geometry_result
        }

    # -------------------------------------------------
    # 2️⃣ NDVI Validation
    # -------------------------------------------------
    ndvi_result = validate_ndvi(request.polygon)

    # Hard vegetation rejection
    if ndvi_result["agriculture_score"] < 0.15:
        return {
            "decision": "FAIL",
            "reason": "Insufficient vegetation detected",
            "geometry": geometry_result,
            "ndvi": ndvi_result
        }

    # -------------------------------------------------
    # 3️⃣ Land Use Classification
    # -------------------------------------------------
    landuse_result = compute_land_use_score(request.polygon)

    # -------------------------------------------------
    # 4️⃣ Crop Plausibility Engine
    # -------------------------------------------------
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

    # -------------------------------------------------
    # 5️⃣ Overlap Detection (Fraud Check)
    # -------------------------------------------------
    overlap_result = compute_overlap_score(
        request.polygon,
        request.farmer_id
    )

    # Hard fraud rejection
    if overlap_result["severity"] == "critical":
        return {
            "decision": "FAIL",
            "reason": "Severe land overlap detected",
            "geometry": geometry_result,
            "ndvi": ndvi_result,
            "land_use": landuse_result,
            "crop_engine": crop_result,
            "overlap": overlap_result
        }

    if overlap_result["severity"] == "fraud_risk":
        return {
            "decision": "REVIEW",
            "reason": "Potential cross-farmer land conflict",
            "geometry": geometry_result,
            "ndvi": ndvi_result,
            "land_use": landuse_result,
            "crop_engine": crop_result,
            "overlap": overlap_result
        }

    #cath
    #  Final Scoring (MCDA Aggregation)

    engine = ScoringEngine(
        weights=SCORING_WEIGHTS,
        threshold=PASS_THRESHOLD
    )

    module_scores = {
        "geometry": geometry_result["geometry_score"],
        "ndvi": ndvi_result["agriculture_score"],
        "land": landuse_result["land_score"],
        "crop": crop_result["crop_score"],
        "overlap": overlap_result["overlap_score"]
    }

    scoring_output = engine.compute(module_scores)

    final_score = scoring_output["final_score"]

    if final_score >= 0.65:
        decision = "PASS"
    elif final_score >= 0.45:
        decision = "REVIEW"
    else:
        decision = "FAIL"
    #cath

    # -------------------------------------------------
    # 8️⃣ Explainability Layer
    # -------------------------------------------------
    explainability_output = generate_explainability(
        geometry_result=geometry_result,
        ndvi_result=ndvi_result,
        landuse_result=landuse_result,
        crop_result=crop_result,
        overlap_result=overlap_result,
        final_score=final_score,
        decision=decision,
        contribution_breakdown=scoring_output["contribution_breakdown"]
    )

    # -------------------------------------------------
    # 9️⃣ Final Response
    # -------------------------------------------------
    return {
        "decision": decision,
        "final_score": final_score,
        "geometry": geometry_result,
        "ndvi": ndvi_result,
        "land_use": landuse_result,
        "crop_engine": crop_result,
        "overlap": overlap_result,
        "explainability": explainability_output
    }