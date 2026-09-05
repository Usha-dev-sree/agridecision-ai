"""
Farm Service - Crop History Model
SQLAlchemy model for farm.crop_history.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class CropHistory(Base):
    __tablename__ = "crop_history"
    __table_args__ = {"schema": "farm"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("farm.farm_plot.id", ondelete="CASCADE"), nullable=False)
    
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    season_name: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Numeric(4, 0), nullable=False)
    
    yield_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    fertilizer_used_summary: Mapped[str | None] = mapped_column(Text)
    pest_issues_summary: Mapped[str | None] = mapped_column(Text)
    
    metadata_col: Mapped[dict | None] = mapped_column("metadata", JSONB, server_default="{}")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
