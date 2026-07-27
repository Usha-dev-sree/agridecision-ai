"""
Farm Service - Kafka Producers
Publishes domain events (e.g., plot created, soil updated) to Kafka.
"""
from typing import Any, Dict

from backend.services.farm_service.src.dependencies import kafka_manager


async def publish_plot_event(event_type: str, plot_id: str, payload: Dict[str, Any]) -> None:
    """Publish a plot-related event to the 'farm.plot.events' topic."""
    message = {
        "event_type": event_type,
        "plot_id": plot_id,
        "payload": payload
    }
    await kafka_manager.publish(
        topic="farm.plot.events",
        message=message,
        key=plot_id
    )

async def publish_device_event(event_type: str, device_id: str, payload: Dict[str, Any]) -> None:
    """Publish a device-related event to the 'farm.device.events' topic."""
    message = {
        "event_type": event_type,
        "device_id": device_id,
        "payload": payload
    }
    await kafka_manager.publish(
        topic="farm.device.events",
        message=message,
        key=device_id
    )
