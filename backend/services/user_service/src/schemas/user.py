"""
User Service - User Schemas
Pydantic DTOs for user profile operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileBase(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    land_holding_ha: Optional[Decimal] = None
    years_of_farming: Optional[int] = None
    education_level: Optional[str] = None


class UserBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    preferred_language: str = "en"
    state_code: str
    district_name: Optional[str] = None
    farmer_type: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: Optional[str] = None
    state_code: Optional[str] = None
    district_name: Optional[str] = None
    farmer_type: Optional[str] = None
    profile: Optional[UserProfileBase] = None


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    agronomist_reg_no: Optional[str] = None
    agronomist_state: Optional[str] = None
    agronomist_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserBase):
    id: UUID
    phone_number: str
    role: str
    account_status: str
    has_verified_phone: bool
    has_verified_agronomist_credential: bool
    referral_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
