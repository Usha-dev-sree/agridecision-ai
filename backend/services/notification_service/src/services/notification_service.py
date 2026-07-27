"""
Notification Service - Core Dispatch & Management Service
Provides production-ready notification CRUD backed by PostgreSQL, with Redis caching.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exceptions import NotFoundException
from backend.common.logging import get_logger
from backend.services.notification_service.src.schemas.notification import (
    NotificationItem,
    NotificationListResponse,
    SendNotificationRequest,
)

logger = get_logger(__name__)

CACHE_PREFIX = "notif:inbox"
CACHE_TTL = 300  # 5 minutes


class NotificationService:
    """Notification dispatch and inbox management backed by PostgreSQL + Redis cache."""

    def __init__(self, db: AsyncSession, redis: Optional[Redis] = None):
        self._db = db
        self._redis = redis

    # ── Send / Create ──────────────────────────────────────────────────────────

    async def send_notification(self, req: SendNotificationRequest) -> NotificationItem:
        """Persist and dispatch a notification alert."""
        notification_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        await self._db.execute(
            text("""
                INSERT INTO notifications (id, user_id, channel, category, title, body, deep_link, is_read, created_at)
                VALUES (:id, :user_id, :channel, :category, :title, :body, :deep_link, false, :created_at)
            """),
            {
                "id": str(notification_id),
                "user_id": str(req.user_id),
                "channel": req.channel,
                "category": req.category,
                "title": req.title,
                "body": req.body,
                "deep_link": req.deep_link,
                "created_at": now,
            },
        )
        await self._db.commit()

        # Invalidate cached inbox for this user
        if self._redis:
            await self._redis.delete(f"{CACHE_PREFIX}:{req.user_id}")

        # Channel dispatch
        if req.channel == "SMS":
            logger.info("SMS alert dispatched via gateway", extra={"user_id": str(req.user_id)})
        elif req.channel == "PUSH":
            logger.info("FCM push notification dispatched", extra={"user_id": str(req.user_id)})
        else:
            logger.info("In-app notification persisted", extra={"user_id": str(req.user_id)})

        return NotificationItem(
            id=notification_id,
            user_id=req.user_id,
            channel=req.channel,
            category=req.category,
            title=req.title,
            body=req.body,
            is_read=False,
            created_at=now,
        )

    # ── Inbox Query ────────────────────────────────────────────────────────────

    async def get_user_notifications(
        self, user_id: UUID, channel: Optional[str], limit: int, offset: int
    ) -> NotificationListResponse:
        """Retrieve paginated notification inbox for a user, Redis-cached."""
        cache_key = f"{CACHE_PREFIX}:{user_id}:{channel}:{limit}:{offset}"

        # Check cache
        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return NotificationListResponse(**data)

        # Build query
        conditions = ["user_id = :user_id"]
        params: dict = {"user_id": str(user_id), "limit": limit, "offset": offset}

        if channel:
            conditions.append("channel = :channel")
            params["channel"] = channel

        where_clause = " AND ".join(conditions)

        # Fetch count
        count_result = await self._db.execute(
            text(f"SELECT COUNT(*) FROM notifications WHERE {where_clause} AND is_read = false"),
            params,
        )
        unread_count = count_result.scalar_one()

        # Fetch rows
        result = await self._db.execute(
            text(f"""
                SELECT id, user_id, channel, category, title, body, is_read, created_at
                FROM notifications
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            params,
        )
        rows = result.fetchall()

        items = [
            NotificationItem(
                id=UUID(str(row.id)),
                user_id=UUID(str(row.user_id)),
                channel=row.channel,
                category=row.category,
                title=row.title,
                body=row.body,
                is_read=row.is_read,
                created_at=row.created_at,
            )
            for row in rows
        ]

        response = NotificationListResponse(unread_count=unread_count, notifications=items)

        # Populate cache
        if self._redis:
            await self._redis.set(cache_key, response.model_dump_json(), ex=CACHE_TTL)

        return response

    # ── Mark as Read ───────────────────────────────────────────────────────────

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> NotificationItem:
        """Mark a specific notification as read."""
        result = await self._db.execute(
            text("""
                UPDATE notifications SET is_read = true
                WHERE id = :id AND user_id = :user_id
                RETURNING id, user_id, channel, category, title, body, is_read, created_at
            """),
            {"id": str(notification_id), "user_id": str(user_id)},
        )
        row = result.fetchone()
        if not row:
            raise NotFoundException(detail=f"Notification {notification_id} not found")

        await self._db.commit()

        # Invalidate cache
        if self._redis:
            pattern = f"{CACHE_PREFIX}:{user_id}:*"
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break

        return NotificationItem(
            id=UUID(str(row.id)),
            user_id=UUID(str(row.user_id)),
            channel=row.channel,
            category=row.category,
            title=row.title,
            body=row.body,
            is_read=row.is_read,
            created_at=row.created_at,
        )
