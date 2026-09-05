"""
User Service - Subscription Models
SQLAlchemy models for iam.subscription and iam.payment_record.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from backend.common.database import Base
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class Subscription(Base):
    __tablename__ = "subscription"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    plan: Mapped[str] = mapped_column(Text, server_default="FREE", nullable=False)
    max_farm_plots: Mapped[int] = mapped_column(SmallInteger, server_default="2", nullable=False)
    max_diagnoses_per_month: Mapped[int] = mapped_column(SmallInteger, server_default="5", nullable=False)
    
    has_market_access: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    has_voice_advisory: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    has_api_access: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    
    billing_period_start: Mapped[date | None] = mapped_column(Date)
    billing_period_end: Mapped[date | None] = mapped_column(Date)
    auto_renew: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PaymentRecord(Base):
    __tablename__ = "payment_record"
    __table_args__ = {"schema": "iam"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.user.id", ondelete="RESTRICT"), nullable=False)
    subscription_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("iam.subscription.id", ondelete="RESTRICT"), nullable=False)
    
    gateway_order_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    gateway_payment_id: Mapped[str | None] = mapped_column(String(100))
    gateway_name: Mapped[str] = mapped_column(String(30), server_default="RAZORPAY", nullable=False)
    
    amount_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="INR", nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default="PENDING", nullable=False)
    plan_purchased: Mapped[str] = mapped_column(Text, nullable=False)
    
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, unique=True)
    gateway_response: Mapped[dict | None] = mapped_column(JSONB, server_default="{}")
    
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
