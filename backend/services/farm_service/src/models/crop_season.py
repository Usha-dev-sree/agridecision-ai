from __future__ import annotations

"""
Farm Service - Crop Season Model
SQLAlchemy model for farm.crop_season.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CropSeason(Base):
    __tablename__ = "crop_season"
    __table_args__ = {"schema": "farm"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farm.farm_plot.id", ondelete="CASCADE"), nullable=False)
    
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_variety: Mapped[str | None] = mapped_column(String(100))
    season_name: Mapped[str] = mapped_column(Text, server_default="KHARIF", nullable=False)
    
    sowing_date: Mapped[date | None] = mapped_column(Date)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date)
    actual_harvest_date: Mapped[date | None] = mapped_column(Date)
    
    target_yield_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    actual_yield_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plot: Mapped[FarmPlot] = relationship("FarmPlot", back_populates="seasons")  # noqa: F821
