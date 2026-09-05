"""
Weather Service - Pydantic Schemas
"""
from datetime import datetime

from pydantic import BaseModel


class WeatherCurrentResponse(BaseModel):
    latitude: float
    longitude: float
    temperature_celsius: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    solar_radiation_mj: float
    evapotranspiration_mm: float
    condition: str
    observed_at: datetime


class DailyForecastItem(BaseModel):
    date: str
    temp_min_celsius: float
    temp_max_celsius: float
    humidity_percent: float
    rainfall_probability_percent: float
    expected_rainfall_mm: float
    wind_speed_kmh: float
    condition: str


class WeatherForecastResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: str | None = "Farm Location"
    forecast_days: list[DailyForecastItem]
    generated_at: datetime


class WeatherAlertResponse(BaseModel):
    alert_id: str
    severity: str  # ADVISORY, WARNING, CRITICAL
    alert_type: str  # HEAVY_RAINFALL, FROST, HEATWAVE, HIGH_WIND
    title: str
    description: str
    effective_from: datetime
    effective_until: datetime
