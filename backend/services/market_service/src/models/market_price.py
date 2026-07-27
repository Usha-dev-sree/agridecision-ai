"""
Market Service - SQLAlchemy Models
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from backend.common.database import Base


class MandiPrice(Base):
    __tablename__ = "mandi_prices"
    __table_args__ = {"schema": "market"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    mandi_name = Column(String(150), nullable=False, index=True)
    commodity = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    arrival_quantity_tonnes = Column(Numeric(10, 2), nullable=False, default=0.0)
    min_price_inr = Column(Numeric(10, 2), nullable=False)
    max_price_inr = Column(Numeric(10, 2), nullable=False)
    modal_price_inr = Column(Numeric(10, 2), nullable=False)
    reported_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
