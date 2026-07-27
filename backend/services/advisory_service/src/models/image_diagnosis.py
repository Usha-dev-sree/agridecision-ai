"""
Advisory Service - Image Diagnosis Model
SQLAlchemy ORM for advisory.image_diagnosis.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.database import Base


class ImageDiagnosis(Base):
    __tablename__ = "image_diagnosis"
    __table_args__ = {"schema": "advisory", "extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plot_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    # S3 / Object Storage path to the uploaded image
    image_s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    image_content_type: Mapped[str] = mapped_column(String(50), server_default="image/jpeg", nullable=False)

    # Diagnosis results from the ML vision model
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    diagnosis_label: Mapped[Optional[str]] = mapped_column(String(100))
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 3))

    # Structured full results (all predicted classes and probabilities)
    full_diagnosis_result: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Actionable recommendations returned alongside diagnosis
    treatment_recommendations: Mapped[Optional[dict]] = mapped_column(JSONB)

    processing_status: Mapped[str] = mapped_column(
        Text, server_default="PENDING", nullable=False
    )  # PENDING | PROCESSING | COMPLETED | FAILED

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
