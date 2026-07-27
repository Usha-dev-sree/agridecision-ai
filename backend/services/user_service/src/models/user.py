"""
User Service - User Models
SQLAlchemy models for iam.user and iam.user_profile.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(320))
    national_id_hash: Mapped[Optional[str]] = mapped_column(String(64))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # We use String here instead of native Enum for simplicity across DB migrations
    # The actual constraints are enforced at the database level by the Alembic migration
    role: Mapped[str] = mapped_column(Text, server_default="FARMER", nullable=False)
    account_status: Mapped[str] = mapped_column(Text, server_default="PENDING", nullable=False)
    has_verified_phone: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    has_verified_agronomist_credential: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    preferred_language: Mapped[str] = mapped_column(Text, server_default="en", nullable=False)
    
    state_code: Mapped[str] = mapped_column(String(10), nullable=False)
    district_name: Mapped[Optional[str]] = mapped_column(String(100))
    farmer_type: Mapped[Optional[str]] = mapped_column(Text)
    
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    referred_by_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id"))
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profile"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    land_holding_ha: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    years_of_farming: Mapped[Optional[int]] = mapped_column(SmallInteger)
    education_level: Mapped[Optional[str]] = mapped_column(String(50))
    bank_account_hash: Mapped[Optional[str]] = mapped_column(String(64))
    
    agronomist_reg_no: Mapped[Optional[str]] = mapped_column(String(50))
    agronomist_state: Mapped[Optional[str]] = mapped_column(String(10))
    agronomist_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")
