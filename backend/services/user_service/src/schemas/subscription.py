"""
User Service - Subscription Schemas
Pydantic DTOs for subscriptions and payment webhooks.
"""
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionStatusResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    max_farm_plots: int
    max_diagnoses_per_month: int
    has_market_access: bool
    has_voice_advisory: bool
    has_api_access: bool
    billing_period_start: date | None = None
    billing_period_end: date | None = None
    auto_renew: bool
    
    model_config = ConfigDict(from_attributes=True)


class RazorpayWebhookPayload(BaseModel):
    event: str
    contains: list[str]
    payload: dict
    created_at: int
    account_id: str


class PaymentInitiateRequest(BaseModel):
    plan_tier: str
    billing_cycle: str = "ANNUAL"  # MONTHLY or ANNUAL


class PaymentInitiateResponse(BaseModel):
    order_id: str
    amount_inr: Decimal
    currency: str
    key_id: str  # Razorpay public key for frontend
