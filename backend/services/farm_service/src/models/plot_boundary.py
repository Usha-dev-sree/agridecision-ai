from __future__ import annotations

"""
Farm Service - Plot Boundary Model
SQLAlchemy model for farm.plot_boundary using GeoAlchemy2 for PostGIS integration.
"""
from datetime import datetime
from uuid import UUID

from backend.common.database import Base
from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PlotBoundary(Base):
    __tablename__ = "plot_boundary"
    __table_args__ = {"schema": "farm"}

    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farm.farm_plot.id", ondelete="CASCADE"), primary_key=True)
    
    # Store the polygon using WGS84 (SRID 4326)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type='POLYGON', srid=4326, spatial_index=True), nullable=False)
    
    # Original GeoJSON stored for exact fidelity retrieval
    original_geojson: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plot: Mapped[FarmPlot] = relationship("FarmPlot", back_populates="boundary")  # noqa: F821
