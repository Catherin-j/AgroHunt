"""
AgroHunt Backend API
FastAPI application for precision agriculture
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import logging

from .soilgrids_service import fetch_soil_data, SoilGridsError, get_soil_texture_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgroHunt API",
    description="Precision Agriculture API for crop and soil analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class CoordinatesRequest(BaseModel):
    """Request model for coordinate-based queries."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class SoilDataResponse(BaseModel):
    """Response model for soil data."""
    soil_ph: float = Field(..., description="Soil pH value")
    clay: float = Field(..., description="Clay percentage")
    sand: float = Field(..., description="Sand percentage")
    silt: float = Field(..., description="Silt percentage")
    soil_texture: str = Field(..., description="Soil texture classification")
    texture_description: Optional[str] = Field(None, description="Human-readable texture description")


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "service": "AgroHunt API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/soil/query", response_model=SoilDataResponse)
async def get_soil_properties(coords: CoordinatesRequest):
    """
    Fetch soil properties for given coordinates using SoilGrids API.
    
    Args:
        coords: Latitude and longitude coordinates
    
    Returns:
        Soil properties including pH, clay, sand, silt, and texture classification
    
    Raises:
        HTTPException: If coordinates are invalid or API request fails
    """
    try:
        logger.info(f"Fetching soil data for coordinates: {coords.latitude}, {coords.longitude}")
        
        # Fetch soil data
        soil_data = fetch_soil_data(coords.latitude, coords.longitude)
        
        # Add texture description
        soil_data['texture_description'] = get_soil_texture_description(
            soil_data['soil_texture']
        )
        
        logger.info(f"Successfully retrieved soil data: {soil_data['soil_texture']}")
        return soil_data
    
    except ValueError as e:
        logger.error(f"Invalid coordinates: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except SoilGridsError as e:
        logger.error(f"SoilGrids API error: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch soil data: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/soil/query")
async def get_soil_properties_get(latitude: float, longitude: float):
    """
    Fetch soil properties using GET method (alternative endpoint).
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    
    Returns:
        Soil properties including pH, clay, sand, silt, and texture classification
    """
    coords = CoordinatesRequest(latitude=latitude, longitude=longitude)
    return await get_soil_properties(coords)


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
