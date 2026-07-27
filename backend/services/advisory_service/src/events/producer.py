"""
Advisory Service - Kafka Producers
Publishes advisory domain events for notification and analytics consumption.
"""
from typing import Any, Dict

from backend.services.advisory_service.src.dependencies import kafka_manager


async def publish_diagnosis_event(event_type: str, diagnosis_id: str, payload: Dict[str, Any]) -> None:
    """Publish a diagnosis event to the AI worker topic."""
    message = {"event_type": event_type, "diagnosis_id": diagnosis_id, "payload": payload}
    await kafka_manager.publish(
        topic="advisory.diagnosis.events",
        message=message,
        key=diagnosis_id
    )


async def publish_recommendation_event(event_type: str, rec_id: str, payload: Dict[str, Any]) -> None:
    """Publish a crop recommendation event for analytics."""
    message = {"event_type": event_type, "recommendation_id": rec_id, "payload": payload}
    await kafka_manager.publish(
        topic="advisory.recommendation.events",
        message=message,
        key=rec_id
    )
