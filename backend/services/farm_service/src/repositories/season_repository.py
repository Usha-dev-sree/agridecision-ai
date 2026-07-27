"""
Farm Service - Season Repository
Handles database operations for farm.crop_season and farm.crop_history.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.farm_service.src.models.crop_history import CropHistory
from backend.services.farm_service.src.models.crop_season import CropSeason
from backend.services.farm_service.src.schemas.seasons import CropSeasonCreate, CropSeasonUpdate


class SeasonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_plot(self, plot_id: UUID) -> List[CropSeason]:
        stmt = select(CropSeason).where(
            CropSeason.plot_id == plot_id,
            CropSeason.is_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, season_id: UUID) -> Optional[CropSeason]:
        stmt = select(CropSeason).where(CropSeason.id == season_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_season(self, plot_id: UUID, data: CropSeasonCreate) -> CropSeason:
        season = CropSeason(
            plot_id=plot_id,
            **data.model_dump()
        )
        self.session.add(season)
        await self.session.flush()
        return season

    async def update_season(self, season: CropSeason, data: CropSeasonUpdate) -> CropSeason:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(season, key, value)
        await self.session.flush()
        return season

    async def delete_season(self, season: CropSeason) -> None:
        season.is_active = False
        await self.session.flush()

    async def list_history(self, plot_id: UUID) -> List[CropHistory]:
        stmt = select(CropHistory).where(CropHistory.plot_id == plot_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
