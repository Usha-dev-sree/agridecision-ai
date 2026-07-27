"""
Farm Service - Soil Schemas
Pydantic DTOs for soil profile operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SoilProfileUpdate(BaseModel):
    soil_type: Optional[str] = Field(None, max_length=50)
    texture_class: Optional[str] = Field(None, max_length=50)
    ph_level: Optional[Decimal] = Field(None, ge=0, le=14)
    organic_carbon_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    nitrogen_content: Optional[Decimal] = Field(None, ge=0)
    phosphorus_content: Optional[Decimal] = Field(None, ge=0)
    potassium_content: Optional[Decimal] = Field(None, ge=0)
    bulk_density: Optional[Decimal] = Field(None, ge=0)
    source: Optional[str] = Field("LAB_TEST", max_length=50)


class SoilProfileResponse(BaseModel):
    plot_id: UUID
    soil_type: Optional[str] = None
    texture_class: Optional[str] = None
    ph_level: Optional[Decimal] = None
    organic_carbon_percent: Optional[Decimal] = None
    nitrogen_content: Optional[Decimal] = None
    phosphorus_content: Optional[Decimal] = None
    potassium_content: Optional[Decimal] = None
    bulk_density: Optional[Decimal] = None
    source: str
    last_tested_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
