"""
AgriDecision AI - Common Database Configuration (Performance Hardened)
========================================================================
Provides high-throughput async SQLAlchemy engine management with:
  - Connection pooling (pool_size=20, max_overflow=30)
  - pool_pre_ping=True (eliminates stale connection latency spikes)
  - pool_recycle=1800 (prevents memory leaks & firewall drops)
  - Statement caching for asyncpg driver
"""
import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# Shared declarative base for all ORM models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions with production performance tuning."""

    def __init__(self, database_url: str):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self.database_url = database_url

    def init_db(self, pool_size: int = 20, max_overflow: int = 30) -> None:
        """Initialize the async database engine with high-concurrency pooling & caching."""
        connect_args = {}
        if "postgresql" in self.database_url:
            connect_args = {
                "statement_cache_size": 100,
                "prepared_statement_cache_size": 100,
                "timeout": 10.0,
            }

        self._engine = create_async_engine(
            self.database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,       # Health-checks connections before checkout
            pool_recycle=1800,        # Recycles connections every 30 minutes
            pool_timeout=30,          # Wait max 30s for pool availability
            echo=False,
            connect_args=connect_args,
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Prevents unnecessary re-queries after commit
            class_=AsyncSession,
        )

    async def close(self) -> None:
        """Close the database engine gracefully."""
        if self._engine is None:
            raise Exception("DatabaseManager is not initialized")
        await self._engine.dispose()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide a transactional scope around a series of operations."""
        if self._sessionmaker is None:
            raise Exception("DatabaseManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
