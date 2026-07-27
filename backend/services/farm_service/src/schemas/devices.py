"""
Farm Service - Device Schemas
Pydantic DTOs for IoT device operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceRegistration(BaseModel):
    device_uid: str = Field(..., max_length=100)
    device_type: str = Field("SOIL_MOISTURE_SENSOR")
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    installation_lat: Optional[Decimal] = None
    installation_lng: Optional[Decimal] = None


class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    installation_lat: Optional[Decimal] = None
    installation_lng: Optional[Decimal] = None
    is_active: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    id: UUID
    plot_id: Optional[UUID] = None
    device_uid: str
    device_type: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    installation_lat: Optional[Decimal] = None
    installation_lng: Optional[Decimal] = None
    is_active: bool
    last_ping_at: Optional[datetime] = None
    battery_level_percent: Optional[int] = None
    configuration: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
