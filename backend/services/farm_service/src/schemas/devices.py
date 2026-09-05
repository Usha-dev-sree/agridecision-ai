"""
Farm Service - Device Schemas
Pydantic DTOs for IoT device operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceRegistration(BaseModel):
    device_uid: str = Field(..., max_length=100)
    device_type: str = Field("SOIL_MOISTURE_SENSOR")
    manufacturer: str | None = Field(None, max_length=100)
    model_number: str | None = Field(None, max_length=100)
    installation_lat: Decimal | None = None
    installation_lng: Decimal | None = None


class DeviceUpdate(BaseModel):
    device_type: str | None = None
    installation_lat: Decimal | None = None
    installation_lng: Decimal | None = None
    is_active: bool | None = None
    configuration: dict[str, Any] | None = None


class DeviceResponse(BaseModel):
    id: UUID
    plot_id: UUID | None = None
    device_uid: str
    device_type: str
    manufacturer: str | None = None
    model_number: str | None = None
    installation_lat: Decimal | None = None
    installation_lng: Decimal | None = None
    is_active: bool
    last_ping_at: datetime | None = None
    battery_level_percent: int | None = None
    configuration: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
