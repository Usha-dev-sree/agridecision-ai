"""
User Service - Consent Model
SQLAlchemy model for iam.consent_record.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.database import Base


class ConsentRecord(Base):
    __tablename__ = "consent_record"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="CASCADE"), nullable=False)
    
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    is_granted: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    metadata_col: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, server_default="{}")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
