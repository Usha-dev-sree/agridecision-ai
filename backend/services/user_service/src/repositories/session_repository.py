"""
User Service - Session & OTP Repository
Handles Redis operations for HMAC-hashed OTPs and Postgres operations for User Sessions.
"""
from datetime import datetime, timezone
from uuid import UUID

from backend.common.security import hash_otp, verify_otp_hash
from backend.services.user_service.src.models.session import UserSession
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.redis = redis

    # --- OTP Redis Operations (HMAC-SHA256 hashed storage) ---
    async def save_otp(self, phone_number: str, otp: str, ttl_seconds: int, secret_key: str = "default_otp_secret") -> None:
        key = f"otp:{phone_number}"
        hashed = hash_otp(otp, secret_key)
        await self.redis.setex(key, ttl_seconds, hashed)

    async def verify_otp(self, phone_number: str, candidate_otp: str, secret_key: str = "default_otp_secret") -> bool:
        key = f"otp:{phone_number}"
        stored_hash = await self.redis.get(key)
        if not stored_hash:
            return False
        return verify_otp_hash(candidate_otp, stored_hash, secret_key)

    async def get_otp(self, phone_number: str) -> str | None:
        """Deprecated: use verify_otp for timing-attack safe comparison."""
        key = f"otp:{phone_number}"
        return await self.redis.get(key)

    async def delete_otp(self, phone_number: str) -> None:
        key = f"otp:{phone_number}"
        await self.redis.delete(key)

    async def increment_lockout(self, phone_number: str, lockout_ttl: int = 900) -> int:
        key = f"otp_lockout:{phone_number}"
        attempts = await self.redis.incr(key)
        if attempts == 1:
            await self.redis.expire(key, lockout_ttl)
        return int(attempts)
        
    async def get_lockout_count(self, phone_number: str) -> int:
        key = f"otp_lockout:{phone_number}"
        count = await self.redis.get(key)
        return int(count) if count else 0

    # --- JWT Postgres Operations ---
    async def create_session(
        self, user_id: UUID, refresh_token_hash: str, expires_at: datetime,
        device_fingerprint: str | None = None, device_platform: str | None = None,
        ip_address: str | None = None, user_agent: str | None = None
    ) -> UserSession:
        user_session = UserSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_fingerprint=device_fingerprint,
            device_platform=device_platform,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )
        self.session.add(user_session)
        await self.session.flush()
        return user_session

    async def get_session_by_token(self, refresh_token_hash: str) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.refresh_token_hash == refresh_token_hash,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now(timezone.utc)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_session(self, session_id: UUID) -> None:
        stmt = update(UserSession).where(UserSession.id == session_id).values(is_active=False)
        await self.session.execute(stmt)

    # --- JWT Blacklist Operations (Redis) ---
    async def blacklist_token(self, token_hash: str, ttl_seconds: int) -> None:
        key = f"token_blacklist:{token_hash}"
        await self.redis.setex(key, ttl_seconds, "1")

    async def is_token_blacklisted(self, token_hash: str) -> bool:
        key = f"token_blacklist:{token_hash}"
        return await self.redis.exists(key) > 0
