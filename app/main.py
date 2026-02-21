from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PlotRequest

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

    if not request.polygon:
        raise HTTPException(
            status_code=400,
            detail="Polygon data is required"
        )

    return {
        "farmer_id": request.farmer_id,
        "crop": request.crop,
        "status": "Request validated"
    }