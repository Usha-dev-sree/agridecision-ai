"""
Farm Service - Season Schemas
Pydantic DTOs for crop season and history.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CropSeasonCreate(BaseModel):
    crop_name: str = Field(..., max_length=100)
    crop_variety: Optional[str] = Field(None, max_length=100)
    season_name: str = Field("KHARIF")
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    target_yield_kg: Optional[Decimal] = Field(None, ge=0)


class CropSeasonUpdate(BaseModel):
    crop_name: Optional[str] = Field(None, max_length=100)
    crop_variety: Optional[str] = Field(None, max_length=100)
    season_name: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    target_yield_kg: Optional[Decimal] = Field(None, ge=0)
    actual_yield_kg: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CropSeasonResponse(BaseModel):
    id: UUID
    plot_id: UUID
    crop_name: str
    crop_variety: Optional[str] = None
    season_name: str
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    target_yield_kg: Optional[Decimal] = None
    actual_yield_kg: Optional[Decimal] = None
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
    yield_kg: Optional[Decimal] = None
    fertilizer_used_summary: Optional[str] = None
    pest_issues_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
