from __future__ import annotations

"""
Farm Service - Soil Profile Model
SQLAlchemy model for farm.soil_profile.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from backend.common.database import Base
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SoilProfile(Base):
    __tablename__ = "soil_profile"
    __table_args__ = {"schema": "farm"}

    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farm.farm_plot.id", ondelete="CASCADE"), primary_key=True)
    
    # Text classification
    soil_type: Mapped[str | None] = mapped_column(String(50))
    texture_class: Mapped[str | None] = mapped_column(String(50))
    
    # SoilGrids data / Lab data
    ph_level: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    organic_carbon_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    nitrogen_content: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    phosphorus_content: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    potassium_content: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    bulk_density: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    
    source: Mapped[str] = mapped_column(Text, server_default="SOILGRIDS_ESTIMATE", nullable=False)
    
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plot: Mapped[FarmPlot] = relationship("FarmPlot", back_populates="soil_profile")  # noqa: F821
