"""
Advisory Service - Irrigation Router
"""
from datetime import date
from uuid import UUID

from backend.services.advisory_service.src.clients.farm_client import FarmServiceClient
from backend.services.advisory_service.src.clients.weather_client import WeatherClient
from backend.services.advisory_service.src.dependencies import get_current_user, get_db
from backend.services.advisory_service.src.repositories.irrigation_repository import (
    IrrigationRepository,
)
from backend.services.advisory_service.src.schemas.irrigation import (
    IrrigationRequest,
    IrrigationScheduleDetail,
    IrrigationScheduleResponse,
)
from backend.services.advisory_service.src.services.irrigation_service import IrrigationService
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/advisory/irrigation", tags=["Irrigation"])


def get_irrigation_service(session: AsyncSession = Depends(get_db)) -> IrrigationService:
    repo = IrrigationRepository(session)
    farm_client = FarmServiceClient()
    weather_client = WeatherClient()
    return IrrigationService(repo, farm_client, weather_client)


@router.post("/schedule", response_model=IrrigationScheduleResponse, status_code=status.HTTP_201_CREATED)
async def generate_irrigation_schedule(
    request: Request,
    data: IrrigationRequest,
    crop_name: str | None = Query(None, description="Planted crop name for Kc lookup"),
    current_user: dict = Depends(get_current_user),
    service: IrrigationService = Depends(get_irrigation_service),
):
    """
    Generate a FAO-56 Penman-Monteith irrigation schedule.
    Fetches live weather forecast from Open-Meteo using the plot's centroid.
    """
    user_id = UUID(current_user["sub"])
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return await service.generate_schedule(user_id, data, access_token, crop_name)


@router.get("/plots/{plot_id}", response_model=list[IrrigationScheduleDetail])
async def get_plot_schedule(
    plot_id: UUID,
    from_date: date | None = Query(None),
    current_user: dict = Depends(get_current_user),
    service: IrrigationService = Depends(get_irrigation_service),
):
    """Get persisted irrigation schedules for a plot."""
    user_id = UUID(current_user["sub"])
    records = await service.get_schedule(plot_id, user_id, from_date)
    return [IrrigationScheduleDetail.model_validate(r) for r in records]
