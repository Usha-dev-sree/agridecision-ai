"""
Advisory Service - Irrigation Schedule Model
SQLAlchemy ORM for advisory.irrigation_schedule.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import Boolean, Date, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedule"
    __table_args__ = {"schema": "advisory", "extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    crop_season_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))

    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Penman-Monteith ETo calculated by the irrigation engine
    eto_mm_day: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    # Crop coefficient applied to ETo
    kc_value: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))

    # Net irrigation requirement
    etc_mm_day: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    recommended_water_mm: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Source weather data used (snapshot for audit)
    weather_input_snapshot: Mapped[dict | None] = mapped_column(JSONB)

    is_applied: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
