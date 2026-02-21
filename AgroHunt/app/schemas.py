from pydantic import BaseModel
from typing import Dict

class PlotRequest(BaseModel):
    farmer_id: str
    crop: str
    polygon: Dict