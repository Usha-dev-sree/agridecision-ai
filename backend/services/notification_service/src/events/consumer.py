"""
Notification Service - Kafka Event Consumer
Consumes events from weather, market, and farm services to dispatch notifications.
Uses one KafkaConsumerRunner per topic.
"""
import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from redis.asyncio import Redis

from backend.common.database import DatabaseManager
from backend.common.kafka import KafkaConsumerRunner
from backend.common.logging import get_logger

logger = get_logger(__name__)

# Idempotency key TTL (24 hours)
IDEMPOTENCY_TTL = 86400


async def _is_duplicate(redis: Redis, event_id: str) -> bool:
    """Check Redis for idempotent event processing. Returns True if already processed."""
    key = f"notification:processed:{event_id}"
    was_set = await redis.set(key, "1", ex=IDEMPOTENCY_TTL, nx=True)
    return not was_set


async def _persist_notification(
    db_manager: DatabaseManager,
    user_id: str,
    channel: str,
    title: str,
    body: str,
    metadata: dict[str, Any],
) -> None:
    """Write notification record to PostgreSQL notifications table."""
    async with db_manager.session() as session:
        from sqlalchemy import text

        await session.execute(
            text("""
                INSERT INTO notifications (user_id, channel, title, body, metadata, status, created_at)
                VALUES (:user_id, :channel, :title, :body, :metadata, 'DELIVERED', :created_at)
            """),
            {
                "user_id": user_id,
                "channel": channel,
                "title": title,
                "body": body,
                "metadata": json.dumps(metadata),
                "created_at": datetime.now(UTC),
            },
        )
        await session.commit()


async def _handle_weather_alert(event: dict[str, Any], db_manager: DatabaseManager, redis: Redis) -> None:
    """Process a weather alert event and dispatch notifications to affected farm users."""
    event_id = f"weather:{event.get('alert_type')}:{event.get('latitude')}:{event.get('longitude')}"
    if await _is_duplicate(redis, event_id):
        logger.debug("Duplicate weather alert skipped", extra={"event_id": event_id})
        return

    severity = event.get("severity", "MODERATE")
    alert_type = event.get("alert_type", "UNKNOWN")
    description = event.get("description", "Weather alert for your farm region")

    title = f"Weather Alert: {alert_type}"
    body = f"[{severity}] {description}"

    try:
        await _persist_notification(
            db_manager, user_id="broadcast", channel="IN_APP", title=title, body=body, metadata=event,
        )
        logger.info("Weather alert notification persisted", extra={"alert_type": alert_type, "severity": severity})
    except Exception as e:
        logger.error("Failed to persist weather alert notification", extra={"error": str(e)})


async def _handle_market_price_update(event: dict[str, Any], db_manager: DatabaseManager, redis: Redis) -> None:
    """Process a market price update event and dispatch notifications to interested users."""
    commodity = event.get("commodity", "Unknown")
    price_change = event.get("price_change_pct", 0.0)

    # Only notify on significant price movements (>5%)
    if abs(price_change) < 5.0:
        return

    event_id = f"market:{commodity}:{event.get('mandi_name')}:{event.get('modal_price')}"
    if await _is_duplicate(redis, event_id):
        return

    direction = "UP" if price_change > 0 else "DOWN"
    title = f"Price Alert: {commodity}"
    body = f"{commodity} prices moved {direction} by {abs(price_change):.1f}% at {event.get('mandi_name', 'Mandi')}"

    try:
        await _persist_notification(
            db_manager, user_id="broadcast", channel="IN_APP", title=title, body=body, metadata=event,
        )
        logger.info("Market price alert notification persisted", extra={"commodity": commodity, "change_pct": price_change})
    except Exception as e:
        logger.error("Failed to persist market notification", extra={"error": str(e)})


async def _handle_farm_event(event: dict[str, Any], db_manager: DatabaseManager, redis: Redis) -> None:
    """Process a generic farm event (e.g., harvest reminder, season start)."""
    event_type = event.get("event_type", "FARM_EVENT")
    event_id = f"farm:{event_type}:{event.get('farm_id')}:{event.get('timestamp', '')}"
    if await _is_duplicate(redis, event_id):
        return

    user_id = event.get("user_id", "broadcast")
    title = event.get("title", f"Farm Update: {event_type}")
    body = event.get("description", "You have a new farm activity update.")

    try:
        await _persist_notification(
            db_manager, user_id=user_id, channel="IN_APP", title=title, body=body, metadata=event,
        )
        logger.info("Farm event notification persisted", extra={"event_type": event_type})
    except Exception as e:
        logger.error("Failed to persist farm event notification", extra={"error": str(e)})


def _build_handler(topic: str, db_manager: DatabaseManager, redis: Redis):
    """Build a handler function for a specific topic, compatible with KafkaConsumerRunner."""
    _topic_handlers = {
        "agri.weather.alert": _handle_weather_alert,
        "agri.market.price_update": _handle_market_price_update,
        "agri.farm.event": _handle_farm_event,
    }
    handler_fn = _topic_handlers.get(topic)

    async def handler(event: dict[str, Any]) -> None:
        if handler_fn:
            await handler_fn(event, db_manager, redis)
        else:
            logger.warning("No handler for topic", extra={"topic": topic})

    return handler


async def start_event_consumer(settings_obj, db_manager: DatabaseManager, redis: Redis) -> None:
    """
    Long-running Kafka consumer loop. Runs as an asyncio background task in the lifespan.
    Spawns one KafkaConsumerRunner per topic using asyncio.gather.
    """
    topics = ["agri.weather.alert", "agri.market.price_update", "agri.farm.event"]

    runners = []
    for topic in topics:
        runner = KafkaConsumerRunner(
            bootstrap_servers=settings_obj.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings_obj.KAFKA_CONSUMER_GROUP_ID,
            topic=topic,
            handler=_build_handler(topic, db_manager, redis),
        )
        runners.append(runner)

    try:
        logger.info("Notification Kafka consumers starting", extra={"topics": topics})
        await asyncio.gather(*(runner.start() for runner in runners))
    except asyncio.CancelledError:
        logger.info("Notification Kafka consumers shutting down gracefully")
        for runner in runners:
            await runner.stop()
    except Exception as e:
        logger.error("Notification Kafka consumer crashed", extra={"error": str(e)})
