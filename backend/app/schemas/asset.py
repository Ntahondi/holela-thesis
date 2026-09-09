"""
Civil Infrastructure Asset Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional

class CivilAsset(BaseModel):
    asset_id: str = Field(..., example="TZ-TANROADS-BR-004")
    name: str = Field(..., example="Tanzanite Bridge")
    structure_type: str = Field(..., example="Extradosed Cable-Stayed Concrete Bridge")
    location_region: str = Field(..., example="Dar es Salaam")
    gps_latitude: float = Field(..., example=-6.8041)
    gps_longitude: float = Field(..., example=39.2906)
    road_class: str = Field(..., example="Trunk")
    year_constructed: int = Field(..., example=2022)
    current_health_index: float = Field(..., example=0.82)
    condition_state: str = Field(..., example="Minor Deterioration")
    importance_factor: float = Field(1.2, example=1.5)
