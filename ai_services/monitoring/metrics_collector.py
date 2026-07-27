"""
AI Services Monitoring - Prometheus Metrics Collector & Prediction Telemetry
Provides Prometheus metrics exposition and prediction log auditing for ML models:
  - Counter: total inferences per model and status
  - Histogram: inference latency distribution (seconds)
  - Gauge: calibrated confidence score tracking
  - Counter: data drift alert events
"""
import time
from typing import Any, Dict, Optional
from backend.common.logging import get_logger

logger = get_logger(__name__)

# Try importing prometheus_client with fallback stub
try:
    from prometheus_client import Counter, Gauge, Histogram

    PREDICTION_COUNT = Counter(
        "agri_ml_predictions_total",
        "Total ML model inference calls",
        ["model_name", "status"]
    )
    PREDICTION_LATENCY = Histogram(
        "agri_ml_prediction_latency_seconds",
        "ML model inference latency distribution in seconds",
        ["model_name"]
    )
    MODEL_CONFIDENCE = Gauge(
        "agri_ml_model_confidence_score",
        "Real-time confidence score of ML inferences",
        ["model_name"]
    )
    DRIFT_EVENTS = Counter(
        "agri_ml_data_drift_events_total",
        "Total statistical feature drift events detected",
        ["feature_name", "severity"]
    )
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logger.info("prometheus_client library missing. Running in simulated telemetry mode.")


class AIMetricsCollector:
    """Telemetry and metrics collector for Triton/Local ML model monitoring."""

    @staticmethod
    def record_inference(model_name: str, duration_seconds: float, confidence_score: float, status: str = "success") -> None:
        """Record an inference event's duration, confidence score, and status."""
        logger.info(
            "ML Inference Telemetry",
            extra={
                "model_name": model_name,
                "latency_ms": round(duration_seconds * 1000.0, 2),
                "confidence_score": round(confidence_score, 4),
                "status": status,
            }
        )

        if HAS_PROMETHEUS:
            PREDICTION_COUNT.labels(model_name=model_name, status=status).inc()
            PREDICTION_LATENCY.labels(model_name=model_name).observe(duration_seconds)
            MODEL_CONFIDENCE.labels(model_name=model_name).set(confidence_score)

    @staticmethod
    def record_drift_event(feature_name: str, psi_score: float, severity: str = "warning") -> None:
        """Record a feature drift alert event."""
        logger.warning(
            "Feature Drift Event Logged",
            extra={"feature_name": feature_name, "psi_score": round(psi_score, 4), "severity": severity}
        )

        if HAS_PROMETHEUS:
            DRIFT_EVENTS.labels(feature_name=feature_name, severity=severity).inc()
