"""
Farm Service - Devices Router
Endpoints for IoT device management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.device_repository import DeviceRepository
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.devices import DeviceRegistration, DeviceResponse, DeviceUpdate
from backend.services.farm_service.src.services.device_service import DeviceService

router = APIRouter(prefix="/v1/plots/{plot_id}/devices", tags=["IoT Devices"])


def get_device_service(session: AsyncSession = Depends(get_db)) -> DeviceService:
    device_repo = DeviceRepository(session)
    plot_repo = PlotRepository(session)
    return DeviceService(device_repo, plot_repo)


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    plot_id: UUID,
    data: DeviceRegistration,
    current_user: dict = Depends(get_current_user),
    device_service: DeviceService = Depends(get_device_service)
):
    owner_id = UUID(current_user["sub"])
    return await device_service.register_device(plot_id, owner_id, data)


@router.get("", response_model=List[DeviceResponse], status_code=status.HTTP_200_OK)
async def list_devices(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    device_service: DeviceService = Depends(get_device_service)
):
    owner_id = UUID(current_user["sub"])
    return await device_service.list_devices(plot_id, owner_id)


@router.get("/{device_id}", response_model=DeviceResponse, status_code=status.HTTP_200_OK)
async def get_device(
    plot_id: UUID,
    device_id: UUID,
    current_user: dict = Depends(get_current_user),
    device_service: DeviceService = Depends(get_device_service)
):
    owner_id = UUID(current_user["sub"])
    return await device_service.get_device(device_id, plot_id, owner_id)


@router.put("/{device_id}", response_model=DeviceResponse, status_code=status.HTTP_200_OK)
async def update_device(
    plot_id: UUID,
    device_id: UUID,
    data: DeviceUpdate,
    current_user: dict = Depends(get_current_user),
    device_service: DeviceService = Depends(get_device_service)
):
    owner_id = UUID(current_user["sub"])
    return await device_service.update_device(device_id, plot_id, owner_id, data)
