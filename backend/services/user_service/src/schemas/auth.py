"""
User Service - Auth Schemas
Pydantic DTOs for authentication.
"""
from typing import Optional

from pydantic import BaseModel, Field, constr


class OTPRequest(BaseModel):
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$") = Field(..., description="E.164 formatted phone number")


class OTPVerify(BaseModel):
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$")
    otp_code: constr(min_length=6, max_length=6)
    device_fingerprint: Optional[str] = None
    device_platform: Optional[str] = "WEB"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
