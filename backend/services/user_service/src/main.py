"""
User Service - Main Entrypoint
FastAPI application initialization, security middleware wiring, and lifecycle events.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.common.exceptions import APIException, api_exception_handler, general_exception_handler
from backend.common.logging import get_logger, setup_logging
from backend.common.middleware.security_middleware import (
    CorrelationIdMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)
from backend.common.metrics import instrument_app
from backend.services.user_service.src.config import settings
from backend.services.user_service.src.dependencies import db_manager, kafka_manager, redis_client
from backend.services.user_service.src.routers import auth, users

setup_logging(settings.APP_NAME, settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up User Service...")
    db_manager.init_db(settings.DB_POOL_SIZE, settings.DB_MAX_OVERFLOW)
    await kafka_manager.start_producer()
    yield
    # Shutdown
    logger.info("Shutting down User Service...")
    await kafka_manager.stop_producer()
    await db_manager.close()
    await redis_client.aclose()


app = FastAPI(
    title="AgriDecision AI - User Service",
    description="Identity, Access Management, and User Profiles",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
)

# Prometheus /metrics endpoint
instrument_app(app)

# Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Security & Infrastructure Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_body_bytes=10 * 1024 * 1024)
app.add_middleware(CorrelationIdMiddleware)

# Restricted CORS Origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "service": settings.APP_NAME}
