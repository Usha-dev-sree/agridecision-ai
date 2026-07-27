"""
User Service - Auth Router
Endpoints for OTP request, verification, and token refresh.
"""
from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.user_service.src.dependencies import get_db, get_redis
from backend.services.user_service.src.repositories.session_repository import SessionRepository
from backend.services.user_service.src.repositories.subscription_repository import SubscriptionRepository
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.auth import OTPRequest, OTPVerify, TokenResponse
from backend.services.user_service.src.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> AuthService:
    user_repo = UserRepository(session)
    session_repo = SessionRepository(session, redis)
    sub_repo = SubscriptionRepository(session)
    return AuthService(user_repo, session_repo, sub_repo)


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(
    request_data: OTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request an OTP for login or registration."""
    # Note: In production, do not return the OTP in the response payload.
    # It is returned here purely for local testing and debugging purposes.
    otp_code = await auth_service.request_otp(request_data.phone_number)
    return {"message": "OTP sent successfully", "debug_otp": otp_code}


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    request: Request,
    verify_data: OTPVerify,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify the OTP and receive JWT tokens."""
    return await auth_service.verify_otp(
        phone_number=verify_data.phone_number,
        otp_code=verify_data.otp_code,
        request=request,
        device_fingerprint=verify_data.device_fingerprint
    )
