"""
IoT Telemetry Service - Main Entrypoint
FastAPI microservice managing IoT device telemetry, sensor data ingestion, and MQTT/Kafka streams.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.common.logging import get_logger, setup_logging
from backend.common.metrics import instrument_app

setup_logging("iot-service", "INFO")
logger = get_logger(__name__)


class TelemetryReading(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: Optional[datetime] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up IoT Telemetry Service...")
    yield
    logger.info("Shutting down IoT Telemetry Service...")


app = FastAPI(
    title="AgriDecision AI - IoT Telemetry Service",
    description="Microservice managing IoT sensor ingestion and real-time telemetry streams.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
)

# Prometheus /metrics endpoint
instrument_app(app)

router = APIRouter(prefix="/v1/iot", tags=["IoT Telemetry"])


@app.get("/health", tags=["System"])
async def root_health_check():
    return {"status": "HEALTHY", "service": "iot-service"}


@router.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "iot-service"}


@router.post("/telemetry", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(reading: TelemetryReading):
    logger.info("Ingested telemetry", extra={"device_id": reading.device_id, "type": reading.sensor_type})
    return {"status": "SUCCESS", "device_id": reading.device_id, "value": reading.value}


app.include_router(router)
