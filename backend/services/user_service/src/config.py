"""
User Service - Environment Configuration
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "user-service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Config
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Config (Session & OTP Cache)
    REDIS_URL: str
    OTP_EXPIRY_SECONDS: int = 300
    MAX_OTP_ATTEMPTS: int = 3

    # Security Config
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
