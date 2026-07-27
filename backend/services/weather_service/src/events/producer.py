"""
Weather Service - Kafka Event Producer
Publishes weather alert events for consumption by notification-service.
"""
from typing import Any, Dict

from backend.common.kafka import KafkaManager
from backend.common.logging import get_logger

logger = get_logger(__name__)

TOPIC_WEATHER_ALERT = "agri.weather.alert"


async def publish_weather_alert(
    kafka: KafkaManager,
    alert_type: str,
    severity: str,
    latitude: float,
    longitude: float,
    description: str,
) -> None:
    """Publish an extreme weather alert event to Kafka for downstream consumers."""
    event: Dict[str, Any] = {
        "event_type": "WEATHER_ALERT",
        "alert_type": alert_type,
        "severity": severity,
        "latitude": latitude,
        "longitude": longitude,
        "description": description,
    }
    await kafka.publish(TOPIC_WEATHER_ALERT, event, key=f"{latitude}:{longitude}")
    logger.info(
        "Weather alert event published",
        extra={"topic": TOPIC_WEATHER_ALERT, "alert_type": alert_type, "severity": severity},
    )
