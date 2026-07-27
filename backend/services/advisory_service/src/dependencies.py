"""
Advisory Service - Dependencies
"""
from fastapi import Request
from redis.asyncio import Redis

from backend.common.database import DatabaseManager
from backend.common.dependencies import get_current_user_dependency, get_db_dependency
from backend.common.kafka import KafkaManager
from backend.services.advisory_service.src.config import settings

db_manager = DatabaseManager(settings.DATABASE_URL)
kafka_manager = KafkaManager(settings.KAFKA_BOOTSTRAP_SERVERS)
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

get_db = get_db_dependency(db_manager)
get_current_user = get_current_user_dependency(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


async def get_redis(request: Request) -> Redis:
    return redis_client
