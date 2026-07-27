"""
User Service - Auth Service
Business logic for OTP generation, verification, and JWT issuance.
Hardened with HMAC-SHA256 OTP hashing, constant-time verification, and timezone-aware datetimes.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Request

from backend.common.exceptions import ConflictException, UnauthorizedException
from backend.common.security import create_access_token, create_refresh_token
from backend.services.user_service.src.config import settings
from backend.services.user_service.src.repositories.session_repository import SessionRepository
from backend.services.user_service.src.repositories.subscription_repository import SubscriptionRepository
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.auth import TokenResponse
from backend.services.user_service.src.schemas.user import UserBase


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        subscription_repo: SubscriptionRepository,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.subscription_repo = subscription_repo

    async def request_otp(self, phone_number: str) -> str:
        """Generate and save an HMAC-hashed OTP. Returns OTP (for dev/SMS distribution)."""
        lockout_count = await self.session_repo.get_lockout_count(phone_number)
        if lockout_count >= settings.MAX_OTP_ATTEMPTS:
            raise ConflictException(detail="Too many failed attempts. Try again later.")

        # CSPRNG for 6-digit OTP
        otp_code = "".join(str(secrets.randbelow(10)) for _ in range(6))
        
        # Save HMAC-SHA256 hashed OTP to Redis
        await self.session_repo.save_otp(phone_number, otp_code, settings.OTP_EXPIRY_SECONDS, secret_key=settings.JWT_SECRET_KEY)
        
        return otp_code

    async def verify_otp(
        self, phone_number: str, otp_code: str, request: Request, device_fingerprint: Optional[str] = None
    ) -> TokenResponse:
        """Verify the OTP in constant time and issue JWT tokens."""
        lockout_count = await self.session_repo.get_lockout_count(phone_number)
        if lockout_count >= settings.MAX_OTP_ATTEMPTS:
            raise ConflictException(detail="Too many failed attempts. Try again later.")

        # Constant-time HMAC comparison
        is_valid = await self.session_repo.verify_otp(phone_number, otp_code, secret_key=settings.JWT_SECRET_KEY)
        
        if not is_valid:
            await self.session_repo.increment_lockout(phone_number)
            raise UnauthorizedException(detail="Invalid or expired OTP")

        # OTP is valid, clear it
        await self.session_repo.delete_otp(phone_number)

        # Get or create user
        user = await self.user_repo.get_by_phone(phone_number)
        if not user:
            user = await self.user_repo.create_user(
                phone_number=phone_number,
                data=UserBase(full_name="New User", state_code="UNKNOWN")
            )
            await self.subscription_repo.create_free_tier(user.id)

        # Generate tokens
        access_token, refresh_token = self._issue_tokens(user.id, user.role)
        
        # Save refresh token session to Postgres
        refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at_days = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 30)
        
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        await self.session_repo.create_session(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_at_days),
            device_fingerprint=device_fingerprint,
            ip_address=client_ip,
            user_agent=user_agent
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def _issue_tokens(self, user_id: UUID, role: str) -> tuple[str, str]:
        access_payload = {"sub": str(user_id), "role": role}
        access_token = create_access_token(
            access_payload, 
            settings.JWT_SECRET_KEY, 
            settings.JWT_ALGORITHM, 
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_payload = {"sub": str(user_id)}
        refresh_token = create_refresh_token(
            refresh_payload,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return access_token, refresh_token
