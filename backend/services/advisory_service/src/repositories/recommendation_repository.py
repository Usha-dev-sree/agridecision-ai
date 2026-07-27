"""
Advisory Service - Recommendation Repository
Handles persistence of crop recommendations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.advisory_service.src.models.crop_recommendation import CropRecommendation


class RecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recommendation: CropRecommendation) -> CropRecommendation:
        self.session.add(recommendation)
        await self.session.flush()
        return recommendation

    async def list_by_plot(self, plot_id: UUID, limit: int = 10) -> List[CropRecommendation]:
        stmt = (
            select(CropRecommendation)
            .where(CropRecommendation.plot_id == plot_id)
            .order_by(CropRecommendation.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, recommendation_id: UUID) -> Optional[CropRecommendation]:
        stmt = select(CropRecommendation).where(CropRecommendation.id == recommendation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
