"""
Advisory Service - Irrigation Schedule Model
SQLAlchemy ORM for advisory.irrigation_schedule.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.database import Base


class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedule"
    __table_args__ = {"schema": "advisory", "extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    crop_season_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))

    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Penman-Monteith ETo calculated by the irrigation engine
    eto_mm_day: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    # Crop coefficient applied to ETo
    kc_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 3))

    # Net irrigation requirement
    etc_mm_day: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    recommended_water_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))

    # Source weather data used (snapshot for audit)
    weather_input_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB)

    is_applied: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
