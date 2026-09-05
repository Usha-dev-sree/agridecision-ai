"""
Farm Service - Season Schemas
Pydantic DTOs for crop season and history.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CropSeasonCreate(BaseModel):
    crop_name: str = Field(..., max_length=100)
    crop_variety: str | None = Field(None, max_length=100)
    season_name: str = Field("KHARIF")
    sowing_date: date | None = None
    expected_harvest_date: date | None = None
    target_yield_kg: Decimal | None = Field(None, ge=0)


class CropSeasonUpdate(BaseModel):
    crop_name: str | None = Field(None, max_length=100)
    crop_variety: str | None = Field(None, max_length=100)
    season_name: str | None = None
    sowing_date: date | None = None
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    target_yield_kg: Decimal | None = Field(None, ge=0)
    actual_yield_kg: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


class CropSeasonResponse(BaseModel):
    id: UUID
    plot_id: UUID
    crop_name: str
    crop_variety: str | None = None
    season_name: str
    sowing_date: date | None = None
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    target_yield_kg: Decimal | None = None
    actual_yield_kg: Decimal | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropHistoryResponse(BaseModel):
    id: UUID
    plot_id: UUID
    crop_name: str
    season_name: str
    year: int
    yield_kg: Decimal | None = None
    fertilizer_used_summary: str | None = None
    pest_issues_summary: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
