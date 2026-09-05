"""
Financial Service - Core Service
Provides credit scoring, loan origination, and loan status queries with PostgreSQL persistence
and Redis caching. Uses the AgroRiskScoringEngine for credit score computation.
"""
import json
import uuid
from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exceptions import NotFoundException
from backend.common.logging import get_logger
from backend.services.financial_service.src.engines.risk_scoring_engine import AgroRiskScoringEngine
from backend.services.financial_service.src.schemas.financial import (
    CreditScoreRequest,
    CreditScoreResponse,
    LoanApplicationRequest,
    LoanApplicationResponse,
)

logger = get_logger(__name__)

CREDIT_CACHE_PREFIX = "financial:credit"
LOAN_CACHE_PREFIX = "financial:loan"
CACHE_TTL = 900  # 15 minutes


class FinancialService:
    """Farm-centric financial services: credit scoring and micro-loan origination."""

    def __init__(self, db: AsyncSession, redis: Redis | None = None):
        self._db = db
        self._redis = redis
        self._engine = AgroRiskScoringEngine()

    # ── Credit Scoring ─────────────────────────────────────────────────────────

    async def calculate_credit_score(self, req: CreditScoreRequest, user_id: str) -> CreditScoreResponse:
        """Calculate agro-financial credit score and persist the evaluation."""
        cache_key = f"{CREDIT_CACHE_PREFIX}:{req.farmer_user_id}:{req.plot_id}"

        # Check cache
        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                return CreditScoreResponse(**json.loads(cached))

        # Compute score
        score, category, max_loan, interest_rate, drivers = self._engine.calculate_credit_score(
            req.total_area_ha, req.soil_health_score, req.historical_yield_avg_kg_ha
        )

        # Persist credit evaluation
        eval_id = uuid.uuid4()
        await self._db.execute(
            text("""
                INSERT INTO credit_evaluations
                    (id, farmer_user_id, plot_id, credit_score, risk_category,
                     max_loan_eligible_inr, interest_rate_pct, evaluated_at)
                VALUES (:id, :farmer_id, :plot_id, :score, :category,
                        :max_loan, :rate, :evaluated_at)
            """),
            {
                "id": str(eval_id),
                "farmer_id": str(req.farmer_user_id),
                "plot_id": req.plot_id,
                "score": score,
                "category": category,
                "max_loan": max_loan,
                "rate": interest_rate,
                "evaluated_at": datetime.now(UTC),
            },
        )
        await self._db.commit()

        response = CreditScoreResponse(
            agri_credit_score=score,
            risk_category=category,
            max_loan_eligible_inr=max_loan,
            interest_rate_percent=interest_rate,
            key_drivers=drivers,
        )

        # Populate cache
        if self._redis:
            await self._redis.set(cache_key, response.model_dump_json(), ex=CACHE_TTL)

        logger.info(
            "Credit score evaluated",
            extra={"farmer_id": str(req.farmer_user_id), "score": score, "category": category},
        )
        return response

    # ── Loan Application ───────────────────────────────────────────────────────

    async def apply_for_loan(self, req: LoanApplicationRequest, user_id: str) -> LoanApplicationResponse:
        """Submit a micro-loan application with EMI calculation and DB persistence."""
        application_id = uuid.uuid4()

        # Fetch latest credit evaluation for this user's plot
        eval_result = await self._db.execute(
            text("""
                SELECT credit_score, risk_category, max_loan_eligible_inr, interest_rate_pct
                FROM credit_evaluations
                WHERE plot_id = :plot_id
                ORDER BY evaluated_at DESC
                LIMIT 1
            """),
            {"plot_id": req.plot_id},
        )
        eval_row = eval_result.fetchone()

        # Determine approval based on credit evaluation
        if eval_row:
            credit_score = eval_row.credit_score
            interest_rate = float(eval_row.interest_rate_pct)
            max_eligible = float(eval_row.max_loan_eligible_inr)

            if req.requested_amount_inr > max_eligible:
                approved_amount = max_eligible
                loan_status = "PARTIALLY_APPROVED"
            elif credit_score < 500:
                approved_amount = 0.0
                loan_status = "REJECTED"
            else:
                approved_amount = req.requested_amount_inr
                loan_status = "APPROVED"
        else:
            # No credit evaluation found — apply conservative defaults
            interest_rate = 12.0
            approved_amount = req.requested_amount_inr * 0.6
            loan_status = "UNDER_REVIEW"

        # Calculate EMI (reducing balance method)
        if approved_amount > 0:
            r = interest_rate / (12 * 100)
            n = req.tenure_months
            emi = approved_amount * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        else:
            emi = 0.0

        # Persist loan application
        await self._db.execute(
            text("""
                INSERT INTO loan_applications
                    (id, user_id, plot_id, requested_amount_inr, approved_amount_inr,
                     purpose, tenure_months, interest_rate_pct, monthly_emi_inr,
                     status, applied_at)
                VALUES (:id, :user_id, :plot_id, :requested, :approved,
                        :purpose, :tenure, :rate, :emi, :status, :applied_at)
            """),
            {
                "id": str(application_id),
                "user_id": user_id,
                "plot_id": req.plot_id,
                "requested": req.requested_amount_inr,
                "approved": round(approved_amount, 2),
                "purpose": req.purpose,
                "tenure": req.tenure_months,
                "rate": interest_rate,
                "emi": round(emi, 2),
                "status": loan_status,
                "applied_at": datetime.now(UTC),
            },
        )
        await self._db.commit()

        logger.info(
            "Loan application processed",
            extra={"application_id": str(application_id), "status": loan_status, "amount": approved_amount},
        )

        return LoanApplicationResponse(
            application_id=application_id,
            status=loan_status,
            approved_amount_inr=round(approved_amount, 2),
            monthly_emi_inr=round(emi, 2),
            interest_rate_percent=interest_rate,
        )

    # ── Loan Status Query ──────────────────────────────────────────────────────

    async def get_loan_status(self, loan_id: UUID, user_id: str) -> LoanApplicationResponse:
        """Retrieve the status of an existing loan application."""
        cache_key = f"{LOAN_CACHE_PREFIX}:{loan_id}"

        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                return LoanApplicationResponse(**json.loads(cached))

        result = await self._db.execute(
            text("""
                SELECT id, status, approved_amount_inr, monthly_emi_inr, interest_rate_pct
                FROM loan_applications
                WHERE id = :loan_id AND user_id = :user_id
            """),
            {"loan_id": str(loan_id), "user_id": user_id},
        )
        row = result.fetchone()

        if not row:
            raise NotFoundException(detail=f"Loan application {loan_id} not found")

        response = LoanApplicationResponse(
            application_id=UUID(str(row.id)),
            status=row.status,
            approved_amount_inr=float(row.approved_amount_inr),
            monthly_emi_inr=float(row.monthly_emi_inr),
            interest_rate_percent=float(row.interest_rate_pct),
        )

        if self._redis:
            await self._redis.set(cache_key, response.model_dump_json(), ex=CACHE_TTL)

        return response
