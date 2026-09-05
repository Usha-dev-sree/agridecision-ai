"""
Advisory Service - Crop Recommendation Model
SQLAlchemy ORM for advisory.crop_recommendation.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class CropRecommendation(Base):
    __tablename__ = "crop_recommendation"
    __table_args__ = {"schema": "advisory", "extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    season_name: Mapped[str] = mapped_column(Text, nullable=False)

    # Top-N recommendations stored as ordered JSON array
    recommendations: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="[]")

    # Input feature snapshot (for auditability and model retraining)
    input_features: Mapped[dict | None] = mapped_column(JSONB, server_default="{}")

    # Confidence score of the top recommendation [0.0 – 1.0]
    top_confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
