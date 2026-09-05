"""
Advisory Service - Weather Client
Fetches weather forecast data from Open-Meteo for irrigation calculations.
"""
from typing import Any

import httpx
from backend.common.exceptions import APIException
from backend.common.logging import get_logger
from backend.services.advisory_service.src.config import settings

logger = get_logger(__name__)


class WeatherClient:
    """HTTP client for Open-Meteo (free, no key required)."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.OPEN_METEO_BASE_URL

    async def get_forecast(
        self, lat: float, lon: float, forecast_days: int = 7
    ) -> list[dict[str, Any]]:
        """
        Fetch hourly/daily weather forecast required for Penman-Monteith ETo.
        Variables: temperature_2m_max, temperature_2m_min, precipitation_sum,
                   windspeed_10m_max, shortwave_radiation_sum, et0_fao_evapotranspiration.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max",
                "shortwave_radiation_sum",
                "et0_fao_evapotranspiration",
            ],
            "forecast_days": forecast_days,
            "timezone": "auto",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/forecast", params=params)
                response.raise_for_status()
                data = response.json()
            except httpx.TimeoutException:
                raise APIException(
                    status_code=503,
                    type_uri="https://api.agridecision.com/errors/weather-timeout",
                    title="Weather Service Unavailable",
                    detail="Timeout fetching weather forecast data",
                )
            except httpx.HTTPStatusError as e:
                raise APIException(
                    status_code=502,
                    type_uri="https://api.agridecision.com/errors/weather-upstream-error",
                    title="Weather Upstream Error",
                    detail=str(e),
                )

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        results = []

        for i, forecast_date in enumerate(dates):
            results.append({
                "date": forecast_date,
                "temp_max_c": daily.get("temperature_2m_max", [None])[i],
                "temp_min_c": daily.get("temperature_2m_min", [None])[i],
                "precipitation_mm": daily.get("precipitation_sum", [None])[i],
                "windspeed_max_kmh": daily.get("windspeed_10m_max", [None])[i],
                "solar_radiation_mj_m2": daily.get("shortwave_radiation_sum", [None])[i],
                # Pre-calculated FAO-56 ETo from Open-Meteo (mm/day) – used as primary source
                "eto_fao_mm_day": daily.get("et0_fao_evapotranspiration", [None])[i],
            })

        logger.debug("Weather forecast fetched", extra={"lat": lat, "lon": lon, "days": forecast_days})
        return results
