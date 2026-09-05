"""
AgriDecision AI - Common FastAPI Dependencies
==============================================
Provides shared dependencies for database sessions, JWT authentication,
and real-time token revocation/blacklisting.
"""
from collections.abc import AsyncGenerator, Callable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.database import DatabaseManager
from backend.common.exceptions import UnauthorizedException
from backend.common.security import decode_token, hash_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/request-otp", auto_error=False)


def get_db_dependency(db_manager: DatabaseManager) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """
    Returns a FastAPI dependency that yields a database session.
    Configured per-service with the service's specific DatabaseManager.
    """
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with db_manager.session() as session:
            yield session
    return get_db


def get_current_user_dependency(
    secret_key: str,
    algorithm: str = "HS256",
    redis_client: Redis | None = None,
) -> Callable:
    """
    Returns a FastAPI dependency that extracts and validates the JWT user payload.
    Checks Redis token blacklist if redis_client is provided (revocation check).
    """
    async def get_current_user(
        request: Request,
        token: str = Depends(oauth2_scheme),
    ) -> dict:
        if not token:
            raise UnauthorizedException(detail="Not authenticated")

        # Check token blacklist in Redis if client is wired
        if redis_client:
            token_digest = hash_token(token)
            is_blacklisted = await redis_client.exists(f"token_blacklist:{token_digest}")
            if is_blacklisted:
                raise UnauthorizedException(detail="Token has been revoked")

        payload = decode_token(token, secret_key, algorithm)
        user_id: str = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(detail="Invalid authentication credentials")

        return payload

    return get_current_user
