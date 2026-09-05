"""
Farm Service - Device Repository
Handles database operations for farm.iot_device.
"""
from uuid import UUID

from backend.services.farm_service.src.models.iot_device import IoTDevice
from backend.services.farm_service.src.schemas.devices import DeviceRegistration, DeviceUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_plot(self, plot_id: UUID) -> list[IoTDevice]:
        stmt = select(IoTDevice).where(
            IoTDevice.plot_id == plot_id,
            IoTDevice.is_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, device_id: UUID) -> IoTDevice | None:
        stmt = select(IoTDevice).where(IoTDevice.id == device_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_by_uid(self, device_uid: str) -> IoTDevice | None:
        stmt = select(IoTDevice).where(IoTDevice.device_uid == device_uid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def register_device(self, plot_id: UUID, data: DeviceRegistration) -> IoTDevice:
        device = IoTDevice(
            plot_id=plot_id,
            **data.model_dump()
        )
        self.session.add(device)
        await self.session.flush()
        return device

    async def update_device(self, device: IoTDevice, data: DeviceUpdate) -> IoTDevice:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(device, key, value)
        await self.session.flush()
        return device
