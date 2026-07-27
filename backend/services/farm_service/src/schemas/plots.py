"""
Farm Service - Plot Schemas
Pydantic DTOs for farm plot and boundary operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlotCreate(BaseModel):
    name: str = Field(..., max_length=100)
    irrigation_type: str = "RAINFED"


class PlotUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    irrigation_type: Optional[str] = None
    is_active: Optional[bool] = None


class GeoJSONGeometry(BaseModel):
    type: str = Field(..., description="Must be 'Polygon'")
    coordinates: List[List[List[float]]] = Field(..., description="Array of linear rings [lon, lat]")


class GeoJSONFeature(BaseModel):
    type: str = Field("Feature", description="Must be 'Feature'")
    geometry: GeoJSONGeometry
    properties: Optional[Dict[str, Any]] = None


class BoundaryResponse(BaseModel):
    plot_id: UUID
    geojson: GeoJSONFeature
    created_at: datetime
    updated_at: datetime


class PlotDetail(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    total_area_ha: Decimal
    irrigation_type: str
    is_active: bool
    centroid_lat: Optional[Decimal] = None
    centroid_lng: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    # Optional nested data depending on query
    boundary: Optional[BoundaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
