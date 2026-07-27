"""
Notification Service - FastAPI Router
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.notification_service.src.schemas.notification import (
    NotificationItem,
    NotificationListResponse,
    SendNotificationRequest,
)
from backend.services.notification_service.src.services.notification_service import NotificationService

router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_user_notifications(
    channel: Optional[str] = Query(None, description="Filter by channel: SMS, PUSH, IN_APP"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Get in-app notifications inbox for logged-in user."""
    user_id = UUID(user_payload["sub"])
    service = NotificationService(db, redis)
    return await service.get_user_notifications(user_id, channel, limit, offset)


@router.post("/send", response_model=NotificationItem, status_code=status.HTTP_201_CREATED)
async def send_notification(
    req: SendNotificationRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Manually send/trigger a notification alert."""
    service = NotificationService(db, redis)
    return await service.send_notification(req)


@router.patch("/{notification_id}/read", response_model=NotificationItem)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(get_current_user),
):
    """Mark a notification as read."""
    user_id = UUID(user_payload["sub"])
    service = NotificationService(db)
    return await service.mark_as_read(notification_id, user_id)
