"""
Farm Service - Plot Schemas
Pydantic DTOs for farm plot and boundary operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlotCreate(BaseModel):
    name: str = Field(..., max_length=100)
    irrigation_type: str = "RAINFED"


class PlotUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    irrigation_type: str | None = None
    is_active: bool | None = None


class GeoJSONGeometry(BaseModel):
    type: str = Field(..., description="Must be 'Polygon'")
    coordinates: list[list[list[float]]] = Field(..., description="Array of linear rings [lon, lat]")


class GeoJSONFeature(BaseModel):
    type: str = Field("Feature", description="Must be 'Feature'")
    geometry: GeoJSONGeometry
    properties: dict[str, Any] | None = None


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
    centroid_lat: Decimal | None = None
    centroid_lng: Decimal | None = None
    created_at: datetime
    updated_at: datetime
    
    # Optional nested data depending on query
    boundary: BoundaryResponse | None = None

    model_config = ConfigDict(from_attributes=True)
