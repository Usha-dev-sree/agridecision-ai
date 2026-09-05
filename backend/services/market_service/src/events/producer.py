"""
Market Service - Kafka Event Producer
Publishes market price update events for downstream consumption.
"""
from typing import Any

from backend.common.kafka import KafkaManager
from backend.common.logging import get_logger

logger = get_logger(__name__)

TOPIC_MARKET_PRICE_UPDATE = "agri.market.price_update"


async def publish_price_update(
    kafka: KafkaManager,
    commodity: str,
    mandi_name: str,
    modal_price: float,
    price_change_pct: float,
) -> None:
    """Publish a market price update event to Kafka."""
    event: dict[str, Any] = {
        "event_type": "MARKET_PRICE_UPDATE",
        "commodity": commodity,
        "mandi_name": mandi_name,
        "modal_price": modal_price,
        "price_change_pct": price_change_pct,
    }
    await kafka.publish(TOPIC_MARKET_PRICE_UPDATE, event, key=commodity)
    logger.info(
        "Market price update event published",
        extra={"topic": TOPIC_MARKET_PRICE_UPDATE, "commodity": commodity},
    )
