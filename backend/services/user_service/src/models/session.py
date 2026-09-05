"""
User Service - Session Model
SQLAlchemy model for iam.user_session.
"""
from datetime import datetime
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class UserSession(Base):
    __tablename__ = "user_session"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="CASCADE"), nullable=False)
    
    refresh_token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    device_fingerprint: Mapped[str | None] = mapped_column(String(200))
    device_platform: Mapped[str | None] = mapped_column(String(20))
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
