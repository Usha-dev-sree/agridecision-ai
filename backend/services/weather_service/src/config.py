"""
Weather Service - Environment Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "weather-service"
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

    # External API Config
    OPENWEATHER_API_KEY: str = "demo-weather-api-key"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # Cache TTLs (seconds)
    CURRENT_WEATHER_CACHE_TTL: int = 1800   # 30 minutes
    FORECAST_CACHE_TTL: int = 10800         # 3 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
