"""
User Service - Subscription Repository
Handles database operations for iam.subscription and iam.payment_record.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.user_service.src.models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_free_tier(self, user_id: UUID) -> Subscription:
        sub = Subscription(
            user_id=user_id,
            plan="FREE",
            max_farm_plots=2,
            max_diagnoses_per_month=5,
            has_market_access=False,
            has_voice_advisory=False,
            has_api_access=False,
            auto_renew=True
        )
        self.session.add(sub)
        await self.session.flush()
        return sub
