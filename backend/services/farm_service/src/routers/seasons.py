"""
Farm Service - Seasons Router
Endpoints for crop season and history management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.repositories.season_repository import SeasonRepository
from backend.services.farm_service.src.schemas.seasons import (
    CropHistoryResponse,
    CropSeasonCreate,
    CropSeasonResponse,
    CropSeasonUpdate,
)
from backend.services.farm_service.src.services.season_service import SeasonService

router = APIRouter(prefix="/v1/plots/{plot_id}/seasons", tags=["Crop Seasons"])


def get_season_service(session: AsyncSession = Depends(get_db)) -> SeasonService:
    season_repo = SeasonRepository(session)
    plot_repo = PlotRepository(session)
    return SeasonService(season_repo, plot_repo)


@router.post("", response_model=CropSeasonResponse, status_code=status.HTTP_201_CREATED)
async def create_season(
    plot_id: UUID,
    data: CropSeasonCreate,
    current_user: dict = Depends(get_current_user),
    season_service: SeasonService = Depends(get_season_service)
):
    owner_id = UUID(current_user["sub"])
    return await season_service.create_season(plot_id, owner_id, data)


@router.get("", response_model=List[CropSeasonResponse], status_code=status.HTTP_200_OK)
async def list_seasons(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    season_service: SeasonService = Depends(get_season_service)
):
    owner_id = UUID(current_user["sub"])
    return await season_service.list_seasons(plot_id, owner_id)


@router.get("/history", response_model=List[CropHistoryResponse], status_code=status.HTTP_200_OK)
async def list_history(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    season_service: SeasonService = Depends(get_season_service)
):
    owner_id = UUID(current_user["sub"])
    return await season_service.list_history(plot_id, owner_id)


@router.get("/{season_id}", response_model=CropSeasonResponse, status_code=status.HTTP_200_OK)
async def get_season(
    plot_id: UUID,
    season_id: UUID,
    current_user: dict = Depends(get_current_user),
    season_service: SeasonService = Depends(get_season_service)
):
    owner_id = UUID(current_user["sub"])
    return await season_service.get_season(season_id, plot_id, owner_id)


@router.put("/{season_id}", response_model=CropSeasonResponse, status_code=status.HTTP_200_OK)
async def update_season(
    plot_id: UUID,
    season_id: UUID,
    data: CropSeasonUpdate,
    current_user: dict = Depends(get_current_user),
    season_service: SeasonService = Depends(get_season_service)
):
    owner_id = UUID(current_user["sub"])
    return await season_service.update_season(season_id, plot_id, owner_id, data)
