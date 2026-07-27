"""
Advisory Service - Environment Configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "advisory-service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Config (advisory schema)
    DATABASE_URL: str = "postgresql+asyncpg://agri:agri@localhost:5432/agridecision"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Config (feature store caching, result caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    ADVISORY_CACHE_TTL_SECONDS: int = 3600  # 1 hour cache for recommendations

    # JWT Config
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Triton Inference Server (internal gRPC) - used for ML model inference
    TRITON_GRPC_URL: str = "triton-inference-server:8001"

    # Farm Service gRPC (for fetching plot/soil data)
    FARM_SERVICE_GRPC_URL: str = "farm-service:50051"

    # External APIs
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
