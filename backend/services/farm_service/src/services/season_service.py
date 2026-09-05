"""
Farm Service - Season Service (Business Logic)
Handles CRUD logic and business rules for crop seasons and history.
"""
from uuid import UUID

from backend.common.exceptions import NotFoundException
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.repositories.season_repository import SeasonRepository
from backend.services.farm_service.src.schemas.seasons import (
    CropHistoryResponse,
    CropSeasonCreate,
    CropSeasonResponse,
    CropSeasonUpdate,
)


class SeasonService:
    def __init__(self, season_repo: SeasonRepository, plot_repo: PlotRepository):
        self.season_repo = season_repo
        self.plot_repo = plot_repo

    async def list_seasons(self, plot_id: UUID, owner_id: UUID) -> list[CropSeasonResponse]:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        seasons = await self.season_repo.list_by_plot(plot_id)
        return [CropSeasonResponse.model_validate(s) for s in seasons]

    async def get_season(self, season_id: UUID, plot_id: UUID, owner_id: UUID) -> CropSeasonResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        season = await self.season_repo.get_by_id(season_id)
        if not season or season.plot_id != plot_id or not season.is_active:
            raise NotFoundException(detail="Season not found")

        return CropSeasonResponse.model_validate(season)

    async def create_season(self, plot_id: UUID, owner_id: UUID, data: CropSeasonCreate) -> CropSeasonResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        season = await self.season_repo.create_season(plot_id, data)
        return CropSeasonResponse.model_validate(season)

    async def update_season(self, season_id: UUID, plot_id: UUID, owner_id: UUID, data: CropSeasonUpdate) -> CropSeasonResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        season = await self.season_repo.get_by_id(season_id)
        if not season or season.plot_id != plot_id or not season.is_active:
            raise NotFoundException(detail="Season not found")

        updated_season = await self.season_repo.update_season(season, data)
        return CropSeasonResponse.model_validate(updated_season)

    async def delete_season(self, season_id: UUID, plot_id: UUID, owner_id: UUID) -> None:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        season = await self.season_repo.get_by_id(season_id)
        if not season or season.plot_id != plot_id or not season.is_active:
            raise NotFoundException(detail="Season not found")

        await self.season_repo.delete_season(season)

    async def list_history(self, plot_id: UUID, owner_id: UUID) -> list[CropHistoryResponse]:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        history = await self.season_repo.list_history(plot_id)
        return [CropHistoryResponse.model_validate(h) for h in history]
