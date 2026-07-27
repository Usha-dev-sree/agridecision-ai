"""
Advisory Service - Irrigation Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IrrigationRequest(BaseModel):
    plot_id: UUID
    crop_season_id: Optional[UUID] = None
    forecast_days: int = Field(7, ge=1, le=14, description="Number of days to generate irrigation schedule for")


class DailyIrrigationEntry(BaseModel):
    schedule_date: date
    eto_mm_day: Decimal
    kc_value: Optional[Decimal] = None
    etc_mm_day: Optional[Decimal] = None
    recommended_water_mm: Optional[Decimal] = None


class IrrigationScheduleResponse(BaseModel):
    plot_id: UUID
    user_id: UUID
    crop_season_id: Optional[UUID] = None
    schedule: List[DailyIrrigationEntry]
    calculation_method: str = "PENMAN_MONTEITH_FAO56"


class IrrigationScheduleDetail(BaseModel):
    id: UUID
    plot_id: UUID
    user_id: UUID
    crop_season_id: Optional[UUID] = None
    schedule_date: date
    eto_mm_day: Decimal
    kc_value: Optional[Decimal] = None
    etc_mm_day: Optional[Decimal] = None
    recommended_water_mm: Optional[Decimal] = None
    weather_input_snapshot: Optional[Dict[str, Any]] = None
    is_applied: bool
    applied_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
