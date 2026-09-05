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
from redis.asyncio import Redis

from backend.common.exceptions import ConflictException, UnauthorizedException
from backend.common.security import create_access_token, create_refresh_token
from backend.services.user_service.src.config import settings
from backend.services.user_service.src.repositories.session_repository import SessionRepository
from backend.services.user_service.src.repositories.subscription_repository import SubscriptionRepository
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.auth import RegisterRequest, TokenResponse
from backend.services.user_service.src.schemas.user import UserBase


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with CSPRNG salt."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + '$' + key.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against PBKDF2-HMAC-SHA256 stored hash."""
    if not stored_hash or '$' not in stored_hash:
        return False
    try:
        salt_hex, key_hex = stored_hash.split('$', 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        subscription_repo: SubscriptionRepository,
        redis_client: Optional[Redis] = None,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.subscription_repo = subscription_repo
        self.redis = redis_client

    async def register_user(self, data: RegisterRequest, request: Request) -> TokenResponse:
        """Register a new unique user with permanent database persistence."""
        # Uniqueness check on phone number
        existing_phone = await self.user_repo.get_by_phone(data.phone_number)
        if existing_phone:
            raise ConflictException(detail="An account with this phone number already exists.")

        # Uniqueness check on email if provided
        if data.email:
            existing_email = await self.user_repo.get_by_email(str(data.email))
            if existing_email:
                raise ConflictException(detail="An account with this email address already exists.")

        # Hash password and create user in Postgres DB
        pwd_hash = hash_password(data.password)
        user = await self.user_repo.create_user_with_password(
            full_name=data.full_name,
            phone_number=data.phone_number,
            email=str(data.email) if data.email else None,
            password_hash=pwd_hash,
            role=data.role or "FARMER",
            state_code=data.state_code,
            district_name=data.district_name,
            farmer_type=data.farmer_type,
            preferred_language=data.preferred_language or "en"
        )
        await self.subscription_repo.create_free_tier(user.id)

        # Issue JWT tokens
        return await self._create_user_session(user, request)

    async def login_with_password(
        self, identifier: str, password: str, request: Request, device_fingerprint: Optional[str] = None
    ) -> TokenResponse:
        """Authenticate user using phone/email and password."""
        user = await self.user_repo.get_by_identifier(identifier)
        if not user:
            raise UnauthorizedException(detail="Invalid phone number/email or password.")

        if not user.password_hash or not verify_password(password, user.password_hash):
            raise UnauthorizedException(detail="Invalid phone number/email or password.")

        return await self._create_user_session(user, request, device_fingerprint)

    async def request_forgot_password(self, email_or_phone: str) -> dict:
        """Request password reset code/token."""
        user = await self.user_repo.get_by_identifier(email_or_phone)
        reset_token = secrets.token_urlsafe(32)
        reset_code = f"{secrets.randbelow(1000000):06d}"

        if user and self.redis:
            # Save token and code mapping to Redis with 15 min TTL
            await self.redis.setex(f"reset_token:{reset_token}", 900, str(user.id))
            await self.redis.setex(f"reset_code:{reset_code}", 900, str(user.id))

        return {
            "message": "Password reset verification code sent.",
            "reset_token": reset_token,
            "reset_code": reset_code,
            "reset_url": f"/v1/auth/ui/reset-password.html?token={reset_token}"
        }

    async def verify_reset_token(self, token_or_code: str) -> dict:
        """Verify password reset token or code."""
        if not self.redis:
            return {"valid": True}
            
        user_id = await self.redis.get(f"reset_token:{token_or_code}") or await self.redis.get(f"reset_code:{token_or_code}")
        if not user_id:
            raise UnauthorizedException(detail="Invalid or expired password reset token.")
            
        return {"valid": True, "token": token_or_code}

    async def reset_password(self, token_or_code: str, new_password: str) -> dict:
        """Reset user password using valid token/code."""
        if not self.redis:
            raise UnauthorizedException(detail="Password reset service unavailable.")

        user_id_str = await self.redis.get(f"reset_token:{token_or_code}") or await self.redis.get(f"reset_code:{token_or_code}")
        if not user_id_str:
            raise UnauthorizedException(detail="Invalid or expired password reset token.")

        user = await self.user_repo.get_by_id(UUID(user_id_str))
        if not user:
            raise UnauthorizedException(detail="User not found.")

        new_hash = hash_password(new_password)
        await self.user_repo.update_password(user, new_hash)

        # Cleanup tokens
        await self.redis.delete(f"reset_token:{token_or_code}")
        await self.redis.delete(f"reset_code:{token_or_code}")

        return {"message": "Password has been reset successfully."}

    async def request_email_verification(self, email: str) -> dict:
        """Request email verification link."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException(detail="User with this email address was not found.")

        token = secrets.token_urlsafe(32)
        if self.redis:
            await self.redis.setex(f"email_verify:{token}", 86400, str(user.id))

        verify_url = f"/v1/auth/ui/verify-email.html?token={token}"
        return {
            "message": "Email verification link generated.",
            "verification_token": token,
            "verification_url": verify_url
        }

    async def verify_email(self, token: str) -> dict:
        """Verify user's email using token."""
        if not self.redis:
            raise UnauthorizedException(detail="Email verification service unavailable.")

        user_id_str = await self.redis.get(f"email_verify:{token}")
        if not user_id_str:
            raise UnauthorizedException(detail="Invalid or expired email verification token.")

        user = await self.user_repo.get_by_id(UUID(user_id_str))
        if not user:
            raise UnauthorizedException(detail="User not found.")

        await self.user_repo.set_email_verified(user, True)
        await self.redis.delete(f"email_verify:{token}")

        return {"message": "Email address verified successfully!", "email": user.email}

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

        return await self._create_user_session(user, request, device_fingerprint)

    async def _create_user_session(
        self, user, request: Request, device_fingerprint: Optional[str] = None
    ) -> TokenResponse:
        access_token, refresh_token = self._issue_tokens(user.id, user.role)
        
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
