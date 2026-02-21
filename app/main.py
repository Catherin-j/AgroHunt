from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PlotRequest
from app.modules.geometry import validate_geometry

app = FastAPI(
    title="Agricultural Plot Validation API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running successfully"}

@app.post("/validate-plot")
def validate_plot(request: PlotRequest):

    geom_result = validate_geometry(request.polygon)

    if not geom_result["valid"]:
        return {
            "decision": "FAIL",
            "details": geom_result
        }

    return {
        "decision": "PASS",
        "geometry": geom_result
    }