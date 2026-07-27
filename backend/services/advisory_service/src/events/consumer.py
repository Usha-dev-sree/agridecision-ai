"""
Advisory Service - Kafka Consumers
Consumes AI worker results and farm boundary change events.
"""
from typing import Any, Dict

from backend.common.kafka import KafkaConsumerRunner
from backend.common.logging import get_logger

logger = get_logger(__name__)


async def handle_diagnosis_result(payload: Dict[str, Any]) -> None:
    """
    Processes ML diagnosis results published by the AI worker pod.
    Updates the ImageDiagnosis record in the DB with the final label and confidence.
    """
    diagnosis_id = payload.get("diagnosis_id")
    label = payload.get("label")
    confidence = payload.get("confidence")
    full_result = payload.get("full_result", {})
    treatments = payload.get("treatment_recommendations", {})

    logger.info(
        "Processing diagnosis result from AI worker",
        extra={"diagnosis_id": diagnosis_id, "label": label, "confidence": confidence}
    )
    # TODO: Inject a DB session and call diagnosis_repository.update_result(...)


async def handle_plot_boundary_changed(payload: Dict[str, Any]) -> None:
    """
    Invalidate recommendation cache when a plot boundary changes significantly.
    """
    plot_id = payload.get("plot_id")
    logger.info("Plot boundary changed – invalidating recommendation cache", extra={"plot_id": plot_id})
    # TODO: Connect to Redis and delete keys matching f"advisory:crop_rec:{plot_id}:*"


def create_diagnosis_result_consumer(bootstrap_servers: str) -> KafkaConsumerRunner:
    return KafkaConsumerRunner(
        bootstrap_servers=bootstrap_servers,
        group_id="advisory-service-diagnosis-results",
        topic="ai.diagnosis.results",
        handler=handle_diagnosis_result
    )


def create_farm_events_consumer(bootstrap_servers: str) -> KafkaConsumerRunner:
    return KafkaConsumerRunner(
        bootstrap_servers=bootstrap_servers,
        group_id="advisory-service-farm-events",
        topic="farm.plot.events",
        handler=handle_plot_boundary_changed
    )
