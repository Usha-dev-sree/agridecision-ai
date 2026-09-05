"""
User Service - Auth Schemas
Pydantic DTOs for authentication.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


class OTPRequest(BaseModel):
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$") = Field(..., description="E.164 formatted phone number")


class OTPVerify(BaseModel):
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$")
    otp_code: constr(min_length=6, max_length=6)
    device_fingerprint: Optional[str] = None
    device_platform: Optional[str] = "WEB"


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$") = Field(..., description="E.164 formatted phone number")
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6, description="Password min 6 characters")
    role: Optional[str] = "FARMER"
    state_code: str = Field("IN-MH", min_length=2, max_length=10)
    district_name: Optional[str] = None
    farmer_type: Optional[str] = "SMALL_COMMERCIAL"
    preferred_language: Optional[str] = "en"


class LoginPasswordRequest(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None  # Accepts phone or email
    password: str = Field(..., min_length=1)
    device_fingerprint: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email_or_phone: str = Field(..., description="Email address or phone number")


class VerifyResetTokenRequest(BaseModel):
    token: str = Field(..., description="Password reset verification token/code")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6)


class RequestEmailVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Email verification token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
