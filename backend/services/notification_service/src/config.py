"""
Notification Service - Environment Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "notification-service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Config
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Config
    REDIS_URL: str

    # Security Config
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Kafka Config
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP_ID: str = "notification-service-group"

    # SMS Gateway
    SMS_GATEWAY_URL: str = "http://localhost:8089/v1/sms/send"
    SMS_GATEWAY_TOKEN: str = "mock_token_for_local_dev"

    # Firebase Push
    FIREBASE_PROJECT_ID: str = "agridecision-local"
    FIREBASE_CREDENTIALS_PATH: str = "./firebase_credentials.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
