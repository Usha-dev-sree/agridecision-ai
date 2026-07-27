"""
Farm Service - Plots Router
Endpoints for plot management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.plots import PlotCreate, PlotDetail, PlotUpdate
from backend.services.farm_service.src.services.plot_service import PlotService

router = APIRouter(prefix="/v1/plots", tags=["Plots"])


def get_plot_service(session: AsyncSession = Depends(get_db)) -> PlotService:
    repo = PlotRepository(session)
    return PlotService(repo)


@router.post("", response_model=PlotDetail, status_code=status.HTTP_201_CREATED)
async def create_plot(
    data: PlotCreate,
    current_user: dict = Depends(get_current_user),
    plot_service: PlotService = Depends(get_plot_service)
):
    owner_id = UUID(current_user["sub"])
    return await plot_service.create_plot(owner_id, data)


@router.get("", response_model=List[PlotDetail], status_code=status.HTTP_200_OK)
async def list_plots(
    current_user: dict = Depends(get_current_user),
    plot_service: PlotService = Depends(get_plot_service)
):
    owner_id = UUID(current_user["sub"])
    return await plot_service.list_plots(owner_id)


@router.get("/{plot_id}", response_model=PlotDetail, status_code=status.HTTP_200_OK)
async def get_plot(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    plot_service: PlotService = Depends(get_plot_service)
):
    owner_id = UUID(current_user["sub"])
    return await plot_service.get_plot(plot_id, owner_id)


@router.put("/{plot_id}", response_model=PlotDetail, status_code=status.HTTP_200_OK)
async def update_plot(
    plot_id: UUID,
    data: PlotUpdate,
    current_user: dict = Depends(get_current_user),
    plot_service: PlotService = Depends(get_plot_service)
):
    owner_id = UUID(current_user["sub"])
    return await plot_service.update_plot(plot_id, owner_id, data)


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    plot_service: PlotService = Depends(get_plot_service)
):
    owner_id = UUID(current_user["sub"])
    await plot_service.delete_plot(plot_id, owner_id)
