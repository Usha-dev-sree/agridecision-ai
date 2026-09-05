"""
Farm Service - Soil Repository
Handles database operations for farm.soil_profile.
"""
from uuid import UUID

from backend.services.farm_service.src.models.soil_profile import SoilProfile
from backend.services.farm_service.src.schemas.soil import SoilProfileUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SoilRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_plot_id(self, plot_id: UUID) -> SoilProfile | None:
        stmt = select(SoilProfile).where(SoilProfile.plot_id == plot_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_profile(self, plot_id: UUID, data: SoilProfileUpdate) -> SoilProfile:
        profile = await self.get_by_plot_id(plot_id)
        
        if profile:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(profile, key, value)
        else:
            profile = SoilProfile(
                plot_id=plot_id,
                **data.model_dump(exclude_unset=True)
            )
            self.session.add(profile)
            
        await self.session.flush()
        return profile
