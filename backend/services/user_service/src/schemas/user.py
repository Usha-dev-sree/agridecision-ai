"""
User Service - User Schemas
Pydantic DTOs for user profile operations.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileBase(BaseModel):
    avatar_url: str | None = None
    bio: str | None = None
    land_holding_ha: Decimal | None = None
    years_of_farming: int | None = None
    education_level: str | None = None


class UserBase(BaseModel):
    full_name: str
    email: EmailStr | None = None
    preferred_language: str = "en"
    state_code: str
    district_name: str | None = None
    farmer_type: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    preferred_language: str | None = None
    state_code: str | None = None
    district_name: str | None = None
    farmer_type: str | None = None
    profile: UserProfileBase | None = None


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    agronomist_reg_no: str | None = None
    agronomist_state: str | None = None
    agronomist_verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserBase):
    id: UUID
    phone_number: str
    role: str
    account_status: str
    has_verified_phone: bool
    has_verified_email: bool = False
    has_verified_agronomist_credential: bool
    referral_code: str | None = None
    created_at: datetime
    updated_at: datetime
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)
