from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import PlotRequest
from app.modules.geometry import validate_geometry
from app.modules.ndvi import validate_ndvi


app = FastAPI(
    title="Agricultural Plot Validation API",
    version="1.0.0"
)

# ----------------------------
# CORS Configuration
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {"message": "API is running successfully"}


# ----------------------------
# Plot Validation Endpoint
# ----------------------------
@app.post("/validate-plot")
def validate_plot(request: PlotRequest):

    # ----------------------------
    # Validate Request
    # ----------------------------
    if not request.polygon:
        raise HTTPException(
            status_code=400,
            detail="Polygon data is required"
        )

    # ==========================================================
    # 1️⃣ GEOMETRY VALIDATION
    # ==========================================================
    geometry_result = validate_geometry(request.polygon)

    if not geometry_result["valid"]:
        return {
            "decision": "FAIL",
            "stage": "geometry_validation",
            "farmer_id": request.farmer_id,
            "crop": request.crop,
            "geometry": geometry_result
        }

    # ==========================================================
    # 2️⃣ NDVI / AGRICULTURAL LAND VALIDATION
    # ==========================================================
    ndvi_result = validate_ndvi(request.polygon)

    # If no imagery available
    if ndvi_result.get("reason") == "No satellite images available":
        return {
            "decision": "FAIL",
            "stage": "ndvi_validation",
            "farmer_id": request.farmer_id,
            "crop": request.crop,
            "geometry": geometry_result,
            "ndvi": ndvi_result
        }

    # If agriculture score too low (likely non-agricultural land)
    if ndvi_result["agriculture_score"] < 0.3:
        return {
            "decision": "FAIL",
            "stage": "ndvi_validation",
            "farmer_id": request.farmer_id,
            "crop": request.crop,
            "geometry": geometry_result,
            "ndvi": ndvi_result
        }

    # ==========================================================
    # 3️⃣ SUCCESS (Geometry + NDVI passed)
    # ==========================================================
    return {
        "decision": "PASS",
        "stage": "ndvi_validation",
        "farmer_id": request.farmer_id,
        "crop": request.crop,
        "geometry": geometry_result,
        "ndvi": ndvi_result
    }