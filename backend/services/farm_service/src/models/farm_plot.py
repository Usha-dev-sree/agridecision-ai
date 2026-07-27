"""
Farm Service - Farm Plot Model
SQLAlchemy model for farm.farm_plot.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.database import Base


class FarmPlot(Base):
    __tablename__ = "farm_plot"
    __table_args__ = {"schema": "farm"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    # user_id comes from IAM service, so no foreign key constraint can be enforced at DB level
    # across logical microservice boundaries, unless we use a shared database.
    # We will assume a shared Postgres instance with isolated schemas, so FK is possible here:
    owner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    irrigation_type: Mapped[str] = mapped_column(Text, server_default="RAINFED", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    # Store centroid for quick distance calculations without loading full geometry
    centroid_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    centroid_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    boundary: Mapped["PlotBoundary"] = relationship("PlotBoundary", back_populates="plot", uselist=False, cascade="all, delete-orphan")
    soil_profile: Mapped["SoilProfile"] = relationship("SoilProfile", back_populates="plot", uselist=False, cascade="all, delete-orphan")
    seasons: Mapped[list["CropSeason"]] = relationship("CropSeason", back_populates="plot", cascade="all, delete-orphan")
    devices: Mapped[list["IoTDevice"]] = relationship("IoTDevice", back_populates="plot")
