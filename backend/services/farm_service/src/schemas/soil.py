"""
Farm Service - Soil Schemas
Pydantic DTOs for soil profile operations.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SoilProfileUpdate(BaseModel):
    soil_type: str | None = Field(None, max_length=50)
    texture_class: str | None = Field(None, max_length=50)
    ph_level: Decimal | None = Field(None, ge=0, le=14)
    organic_carbon_percent: Decimal | None = Field(None, ge=0, le=100)
    nitrogen_content: Decimal | None = Field(None, ge=0)
    phosphorus_content: Decimal | None = Field(None, ge=0)
    potassium_content: Decimal | None = Field(None, ge=0)
    bulk_density: Decimal | None = Field(None, ge=0)
    source: str | None = Field("LAB_TEST", max_length=50)


class SoilProfileResponse(BaseModel):
    plot_id: UUID
    soil_type: str | None = None
    texture_class: str | None = None
    ph_level: Decimal | None = None
    organic_carbon_percent: Decimal | None = None
    nitrogen_content: Decimal | None = None
    phosphorus_content: Decimal | None = None
    potassium_content: Decimal | None = None
    bulk_density: Decimal | None = None
    source: str
    last_tested_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
