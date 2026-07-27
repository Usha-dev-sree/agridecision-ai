"""
Farm Service - IoT Device Model
SQLAlchemy model for farm.iot_device.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.database import Base


class IoTDevice(Base):
    __tablename__ = "iot_device"
    __table_args__ = {"schema": "farm"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farm.farm_plot.id", ondelete="SET NULL"))
    
    device_uid: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    device_type: Mapped[str] = mapped_column(Text, server_default="SOIL_MOISTURE_SENSOR", nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model_number: Mapped[Optional[str]] = mapped_column(String(100))
    
    installation_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    installation_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    last_ping_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    battery_level_percent: Mapped[Optional[int]] = mapped_column(Numeric(3, 0))
    
    configuration: Mapped[Optional[dict]] = mapped_column(JSONB, server_default="{}")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    plot: Mapped["FarmPlot"] = relationship("FarmPlot", back_populates="devices")
