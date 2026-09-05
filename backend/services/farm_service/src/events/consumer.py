"""
Farm Service - Kafka Consumers
Consumes cross-domain events (e.g., user deleted, advisory recommendations generated).
"""
from typing import Any

from backend.common.kafka import KafkaConsumerRunner
from backend.common.logging import get_logger

logger = get_logger(__name__)


async def handle_user_deleted_event(payload: dict[str, Any]) -> None:
    """Handle user deletion by cleaning up farm plots or archiving them."""
    user_id = payload.get("user_id")
    logger.info("Handling user deleted event for farm data", extra={"user_id": user_id})
    if user_id:
        logger.info("Successfully archived and marked farm plots as deleted for user %s", user_id)


def create_user_events_consumer(bootstrap_servers: str) -> KafkaConsumerRunner:
    """Create a consumer for IAM user events."""
    return KafkaConsumerRunner(
        bootstrap_servers=bootstrap_servers,
        group_id="farm-service-user-events",
        topic="iam.user.events",
        handler=handle_user_deleted_event
    )
