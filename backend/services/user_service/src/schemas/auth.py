"""
User Service - Auth Schemas
Pydantic DTOs for authentication.
"""

from pydantic import BaseModel, EmailStr, Field


class OTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", description="E.164 formatted phone number")


class OTPVerify(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    otp_code: str = Field(..., min_length=6, max_length=6)
    device_fingerprint: str | None = None
    device_platform: str | None = "WEB"


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", description="E.164 formatted phone number")
    email: EmailStr | None = None
    password: str = Field(..., min_length=6, description="Password min 6 characters")
    role: str | None = "FARMER"
    state_code: str = Field("IN-MH", min_length=2, max_length=10)
    district_name: str | None = None
    farmer_type: str | None = "SMALL_COMMERCIAL"
    preferred_language: str | None = "en"


class LoginPasswordRequest(BaseModel):
    phone_number: str | None = None
    email: EmailStr | None = None
    username: str | None = None  # Accepts phone or email
    password: str = Field(..., min_length=1)
    device_fingerprint: str | None = None


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
