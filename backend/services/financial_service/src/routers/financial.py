"""
Financial Service - FastAPI Router
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.financial_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.financial_service.src.schemas.financial import (
    CreditScoreRequest,
    CreditScoreResponse,
    LoanApplicationRequest,
    LoanApplicationResponse,
)
from backend.services.financial_service.src.services.financial_service import FinancialService

router = APIRouter(prefix="/v1/financial", tags=["Financial & Credit Scoring"])


@router.post("/credit-score", response_model=CreditScoreResponse)
async def get_credit_score(
    req: CreditScoreRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Evaluate agronomic credit score and loan eligibility limit."""
    service = FinancialService(db, redis)
    return await service.calculate_credit_score(req, user_payload["sub"])


@router.post("/loans/apply", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_loan(
    req: LoanApplicationRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Submit a micro-loan application for agricultural input purchase."""
    service = FinancialService(db, redis)
    return await service.apply_for_loan(req, user_payload["sub"])


@router.get("/loans/{loan_id}", response_model=LoanApplicationResponse)
async def get_loan_status(
    loan_id: UUID,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve the status of an existing loan application."""
    service = FinancialService(db, redis)
    return await service.get_loan_status(loan_id, user_payload["sub"])
