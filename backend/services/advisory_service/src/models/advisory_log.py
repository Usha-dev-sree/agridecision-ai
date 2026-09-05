"""
Advisory Service - Advisory Log Model
SQLAlchemy ORM for advisory.advisory_log (tracks all advisory interactions).
"""
from datetime import datetime
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class AdvisoryLog(Base):
    __tablename__ = "advisory_log"
    __table_args__ = {"schema": "advisory"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    plot_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))

    advisory_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # CROP_RECOMMENDATION | IRRIGATION | DIAGNOSIS | PEST_ALERT | WEATHER_ALERT

    # Reference to the specific advisory record
    reference_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    reference_table: Mapped[str | None] = mapped_column(String(100))

    # The advisory content delivered (for voice/SMS channels this is the text rendered)
    delivery_payload: Mapped[dict | None] = mapped_column(JSONB)

    # Channel through which the advisory was delivered
    channel: Mapped[str] = mapped_column(
        Text, server_default="APP_PUSH", nullable=False
    )  # APP_PUSH | SMS | VOICE | WHATSAPP

    delivery_status: Mapped[str] = mapped_column(
        Text, server_default="SENT", nullable=False
    )  # SENT | DELIVERED | READ | FAILED

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
