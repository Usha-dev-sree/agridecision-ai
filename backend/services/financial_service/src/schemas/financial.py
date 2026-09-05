"""
Financial Service - Pydantic Schemas
"""
from uuid import UUID

from pydantic import BaseModel, Field


class CreditScoreRequest(BaseModel):
    farmer_user_id: UUID
    plot_id: str
    total_area_ha: float
    soil_health_score: float
    historical_yield_avg_kg_ha: float


class CreditScoreResponse(BaseModel):
    agri_credit_score: int  # 300 to 850
    risk_category: str  # LOW_RISK, MODERATE_RISK, HIGH_RISK
    max_loan_eligible_inr: float
    interest_rate_percent: float
    key_drivers: list[str]


class LoanApplicationRequest(BaseModel):
    plot_id: str
    requested_amount_inr: float
    purpose: str = Field("INPUT_PURCHASE", description="INPUT_PURCHASE, IRRIGATION_EQUIPMENT, MACHINERY")
    tenure_months: int = 12


class LoanApplicationResponse(BaseModel):
    application_id: UUID
    status: str  # APPROVED, UNDER_REVIEW, REJECTED
    approved_amount_inr: float
    monthly_emi_inr: float
    interest_rate_percent: float
