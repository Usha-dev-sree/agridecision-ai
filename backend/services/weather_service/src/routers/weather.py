"""
Weather Service - FastAPI Router
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis

from backend.services.weather_service.src.dependencies import get_current_user, get_redis
from backend.services.weather_service.src.schemas.weather import (
    WeatherAlertResponse,
    WeatherCurrentResponse,
    WeatherForecastResponse,
)
from backend.services.weather_service.src.services.weather_service import WeatherService

router = APIRouter(prefix="/v1/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherCurrentResponse)
async def get_current_weather(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve real-time current weather observation for a farm location."""
    service = WeatherService(redis)
    return await service.get_current_weather(latitude, longitude)


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve 7-day agro-meteorological forecast."""
    service = WeatherService(redis)
    return await service.get_7day_forecast(latitude, longitude)


@router.get("/alerts", response_model=List[WeatherAlertResponse])
async def get_weather_alerts(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve active weather alerts (heavy rain, heatwave, frost) for region."""
    service = WeatherService(redis)
    return await service.get_active_alerts(latitude, longitude)
