"""
Analytics Service - Environment Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "analytics-service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Config
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # TimescaleDB (same connection for time-series aggregations)
    TIMESCALE_URL: str = ""

    # Redis Config
    REDIS_URL: str

    # Security Config
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Cache TTLs
    ANALYTICS_CACHE_TTL: int = 600  # 10 minutes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
