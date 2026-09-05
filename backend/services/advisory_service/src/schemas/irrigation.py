"""
Advisory Service - Irrigation Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IrrigationRequest(BaseModel):
    plot_id: UUID
    crop_season_id: UUID | None = None
    forecast_days: int = Field(7, ge=1, le=14, description="Number of days to generate irrigation schedule for")


class DailyIrrigationEntry(BaseModel):
    schedule_date: date
    eto_mm_day: Decimal
    kc_value: Decimal | None = None
    etc_mm_day: Decimal | None = None
    recommended_water_mm: Decimal | None = None


class IrrigationScheduleResponse(BaseModel):
    plot_id: UUID
    user_id: UUID
    crop_season_id: UUID | None = None
    schedule: list[DailyIrrigationEntry]
    calculation_method: str = "PENMAN_MONTEITH_FAO56"


class IrrigationScheduleDetail(BaseModel):
    id: UUID
    plot_id: UUID
    user_id: UUID
    crop_season_id: UUID | None = None
    schedule_date: date
    eto_mm_day: Decimal
    kc_value: Decimal | None = None
    etc_mm_day: Decimal | None = None
    recommended_water_mm: Decimal | None = None
    weather_input_snapshot: dict[str, Any] | None = None
    is_applied: bool
    applied_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
