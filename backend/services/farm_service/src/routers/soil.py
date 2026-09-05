"""
Farm Service - Soil Router
Endpoints for soil profile management.
"""
from uuid import UUID

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.repositories.soil_repository import SoilRepository
from backend.services.farm_service.src.schemas.soil import SoilProfileResponse, SoilProfileUpdate
from backend.services.farm_service.src.services.soil_service import SoilService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/plots/{plot_id}/soil", tags=["Soil"])


def get_soil_service(session: AsyncSession = Depends(get_db)) -> SoilService:
    soil_repo = SoilRepository(session)
    plot_repo = PlotRepository(session)
    return SoilService(soil_repo, plot_repo)


@router.get("", response_model=SoilProfileResponse, status_code=status.HTTP_200_OK)
async def get_soil_profile(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    soil_service: SoilService = Depends(get_soil_service)
):
    owner_id = UUID(current_user["sub"])
    return await soil_service.get_soil_profile(plot_id, owner_id)


@router.put("", response_model=SoilProfileResponse, status_code=status.HTTP_200_OK)
async def update_soil_profile(
    plot_id: UUID,
    data: SoilProfileUpdate,
    current_user: dict = Depends(get_current_user),
    soil_service: SoilService = Depends(get_soil_service)
):
    owner_id = UUID(current_user["sub"])
    return await soil_service.update_soil_profile(plot_id, owner_id, data)
