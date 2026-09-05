"""
AgriDecision AI - Redis Sliding Window Rate Limiter
===================================================
Provides sliding window rate limiting to protect API endpoints against DoS, brute force, and abuse.
"""
import time

from redis.asyncio import Redis

from backend.common.exceptions import APIException


class RateLimiter:
    """Redis-backed sliding window rate limiter."""

    def __init__(self, redis_client: Redis, max_requests: int = 100, window_seconds: int = 60) -> None:
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check_rate_limit(self, identifier: str, cost: int = 1) -> bool:
        """
        Check and increment rate limit for a given client identifier (IP or User ID).
        Raises 429 Too Many Requests if threshold is exceeded.
        """
        now = time.time()
        clear_before = now - self.window_seconds
        key = f"rate_limit:{identifier}"

        async with self.redis.pipeline(transaction=True) as pipe:
            # 1. Remove elements older than window
            pipe.zremrangebyscore(key, 0, clear_before)
            # 2. Add current timestamp
            pipe.zadd(key, {f"{now}:{time.time_ns()}": now})
            # 3. Count remaining
            pipe.zcard(key)
            # 4. Set TTL
            pipe.expire(key, self.window_seconds)
            results = await pipe.execute()

        request_count = results[2]

        if request_count > self.max_requests:
            raise APIException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
            )

        return True
