"""
Farm Service - Device Service (Business Logic)
Handles CRUD logic and business rules for IoT devices.
"""
from typing import List
from uuid import UUID

from backend.common.exceptions import ConflictException, NotFoundException
from backend.services.farm_service.src.repositories.device_repository import DeviceRepository
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.devices import DeviceRegistration, DeviceResponse, DeviceUpdate


class DeviceService:
    def __init__(self, device_repo: DeviceRepository, plot_repo: PlotRepository):
        self.device_repo = device_repo
        self.plot_repo = plot_repo

    async def register_device(self, plot_id: UUID, owner_id: UUID, data: DeviceRegistration) -> DeviceResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        # Check if UID is already registered globally (device UIDs should be unique)
        existing_device = await self.device_repo.get_by_uid(data.device_uid)
        if existing_device:
            raise ConflictException(detail="Device UID is already registered")

        device = await self.device_repo.register_device(plot_id, data)
        return DeviceResponse.model_validate(device)

    async def list_devices(self, plot_id: UUID, owner_id: UUID) -> List[DeviceResponse]:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        devices = await self.device_repo.list_by_plot(plot_id)
        return [DeviceResponse.model_validate(d) for d in devices]

    async def get_device(self, device_id: UUID, plot_id: UUID, owner_id: UUID) -> DeviceResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        device = await self.device_repo.get_by_id(device_id)
        if not device or device.plot_id != plot_id or not device.is_active:
            raise NotFoundException(detail="Device not found")

        return DeviceResponse.model_validate(device)

    async def update_device(self, device_id: UUID, plot_id: UUID, owner_id: UUID, data: DeviceUpdate) -> DeviceResponse:
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        device = await self.device_repo.get_by_id(device_id)
        if not device or device.plot_id != plot_id or not device.is_active:
            raise NotFoundException(detail="Device not found")

        updated_device = await self.device_repo.update_device(device, data)
        return DeviceResponse.model_validate(updated_device)
