"""
Farm Service - Plot Service (Business Logic)
Handles CRUD logic and business rules for farm plots.
"""
from typing import List
from uuid import UUID

from backend.common.exceptions import NotFoundException
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.plots import PlotCreate, PlotDetail, PlotUpdate


class PlotService:
    def __init__(self, plot_repo: PlotRepository):
        self.plot_repo = plot_repo

    async def create_plot(self, owner_id: UUID, data: PlotCreate) -> PlotDetail:
        plot = await self.plot_repo.create_plot(owner_id, data)
        return PlotDetail.model_validate(plot)

    async def get_plot(self, plot_id: UUID, owner_id: UUID) -> PlotDetail:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")
        return PlotDetail.model_validate(plot)

    async def list_plots(self, owner_id: UUID) -> List[PlotDetail]:
        plots = await self.plot_repo.list_by_owner(owner_id)
        return [PlotDetail.model_validate(p) for p in plots]

    async def update_plot(self, plot_id: UUID, owner_id: UUID, data: PlotUpdate) -> PlotDetail:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")
            
        updated_plot = await self.plot_repo.update_plot(plot, data)
        return PlotDetail.model_validate(updated_plot)

    async def delete_plot(self, plot_id: UUID, owner_id: UUID) -> None:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")
            
        await self.plot_repo.delete_plot(plot)
