"""
Notification Service - Pydantic Schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SendNotificationRequest(BaseModel):
    user_id: UUID
    channel: str = Field("PUSH", description="PUSH, SMS, EMAIL, IN_APP")
    category: str = Field("DISEASE_ALERT", description="DISEASE_ALERT, WEATHER_WARNING, MARKET_PRICE, ADVISORY")
    title: str
    body: str
    deep_link: Optional[str] = None


class NotificationItem(BaseModel):
    id: UUID
    user_id: UUID
    channel: str
    category: str
    title: str
    body: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: List[NotificationItem]
