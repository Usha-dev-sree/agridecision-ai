"""
Farm Service - Soil Service (Business Logic)
Handles CRUD logic and business rules for soil profiles.
"""
from uuid import UUID

from backend.common.exceptions import NotFoundException
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.repositories.soil_repository import SoilRepository
from backend.services.farm_service.src.schemas.soil import SoilProfileResponse, SoilProfileUpdate


class SoilService:
    def __init__(self, soil_repo: SoilRepository, plot_repo: PlotRepository):
        self.soil_repo = soil_repo
        self.plot_repo = plot_repo

    async def get_soil_profile(self, plot_id: UUID, owner_id: UUID) -> SoilProfileResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        profile = await self.soil_repo.get_by_plot_id(plot_id)
        if not profile:
            raise NotFoundException(detail="Soil profile not found for this plot")
            
        return SoilProfileResponse.model_validate(profile)

    async def update_soil_profile(self, plot_id: UUID, owner_id: UUID, data: SoilProfileUpdate) -> SoilProfileResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        # In a real scenario, if source == SOILGRIDS_ESTIMATE, we would trigger an external API
        # call to SoilGrids here using the plot's centroid_lat/lng.

        profile = await self.soil_repo.upsert_profile(plot_id, data)
        return SoilProfileResponse.model_validate(profile)
