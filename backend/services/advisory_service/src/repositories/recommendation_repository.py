"""
Advisory Service - Recommendation Repository
Handles persistence of crop recommendations.
"""
from uuid import UUID

from backend.services.advisory_service.src.models.crop_recommendation import CropRecommendation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recommendation: CropRecommendation) -> CropRecommendation:
        self.session.add(recommendation)
        await self.session.flush()
        return recommendation

    async def list_by_plot(self, plot_id: UUID, limit: int = 10) -> list[CropRecommendation]:
        stmt = (
            select(CropRecommendation)
            .where(CropRecommendation.plot_id == plot_id)
            .order_by(CropRecommendation.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, recommendation_id: UUID) -> CropRecommendation | None:
        stmt = select(CropRecommendation).where(CropRecommendation.id == recommendation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
