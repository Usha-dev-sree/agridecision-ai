"""
Advisory Service - Irrigation Engine
Implements the FAO-56 Penman-Monteith reference evapotranspiration (ETo) formula.
Used to calculate daily irrigation water requirements for a given farm plot.
Reference: Allen et al., 1998 – FAO Irrigation and Drainage Paper No. 56.
"""
import math
from datetime import date
from typing import Any

from backend.common.logging import get_logger

logger = get_logger(__name__)

# Crop coefficient (Kc) lookup table per growth stage.
# A full implementation would use FAO-56 Annex 8 tables per crop/growth stage/season.
# These are representative mid-season Kc values for common Indian crops.
KC_TABLE: dict[str, float] = {
    "rice": 1.20,
    "wheat": 1.15,
    "maize": 1.20,
    "cotton": 1.15,
    "soybean": 1.15,
    "sugarcane": 1.25,
    "groundnut": 1.15,
    "sunflower": 1.10,
    "default": 1.00,
}


def get_kc_for_crop(crop_name: str) -> float:
    """Look up the mid-season crop coefficient for a given crop."""
    return KC_TABLE.get(crop_name.lower(), KC_TABLE["default"])


def compute_eto_penman_monteith(
    temp_max_c: float,
    temp_min_c: float,
    solar_radiation_mj_m2: float,
    wind_speed_ms: float,
    humidity_percent: float,
    elevation_m: float = 200.0,
) -> float:
    """
    Compute FAO-56 Penman-Monteith Reference Evapotranspiration (ETo).

    Args:
        temp_max_c: Maximum daily temperature (°C)
        temp_min_c: Minimum daily temperature (°C)
        solar_radiation_mj_m2: Solar radiation (MJ/m²/day)
        wind_speed_ms: Mean daily wind speed at 2m height (m/s)
        humidity_percent: Mean relative humidity (%)
        elevation_m: Elevation above sea level (m), affects atmospheric pressure

    Returns:
        ETo in mm/day
    """
    T_mean = (temp_max_c + temp_min_c) / 2.0

    # 1. Saturation vapour pressure (kPa)
    e_s_max = 0.6108 * math.exp((17.27 * temp_max_c) / (temp_max_c + 237.3))
    e_s_min = 0.6108 * math.exp((17.27 * temp_min_c) / (temp_min_c + 237.3))
    e_s = (e_s_max + e_s_min) / 2.0

    # 2. Actual vapour pressure (kPa) from humidity
    e_a = (humidity_percent / 100.0) * e_s

    # 3. Slope of saturation vapour pressure curve Δ (kPa/°C)
    delta = 4098.0 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3))) / ((T_mean + 237.3) ** 2)

    # 4. Atmospheric pressure P (kPa) from elevation
    P = 101.3 * ((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26

    # 5. Psychrometric constant γ (kPa/°C)
    gamma = 0.000665 * P

    # 6. Net radiation (Rn) approximation: Rn ≈ 0.77 * Rs (simple approach; full FAO56 uses Rns + Rnl)
    Rn = 0.77 * solar_radiation_mj_m2

    # 7. Soil heat flux G (MJ/m²/day): daily G ≈ 0 (FAO-56 simplification for daily ETo)
    G = 0.0

    # 8. Penman-Monteith ETo (mm/day)
    numerator = (0.408 * delta * (Rn - G)) + (gamma * (900.0 / (T_mean + 273)) * wind_speed_ms * (e_s - e_a))
    denominator = delta + gamma * (1.0 + 0.34 * wind_speed_ms)

    ETo = numerator / denominator
    return max(0.0, ETo)


def calculate_irrigation_schedule(
    weather_forecast: list[dict[str, Any]],
    crop_name: str | None = None,
    elevation_m: float = 200.0,
    humidity_percent: float = 70.0,
) -> list[dict[str, Any]]:
    """
    Calculate a multi-day irrigation schedule from weather forecast data.

    Args:
        weather_forecast: List of daily weather dicts from WeatherClient.
        crop_name: The planted crop (used to look up Kc coefficient).
        elevation_m: Plot elevation for atmospheric pressure calculation.
        humidity_percent: Estimated mean relative humidity (%).

    Returns:
        A list of daily irrigation recommendation dicts.
    """
    kc = get_kc_for_crop(crop_name) if crop_name else 1.0
    schedule = []

    for day_data in weather_forecast:
        raw_date = day_data.get("date")
        schedule_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date

        # Use Open-Meteo's pre-calculated FAO ETo if available (most accurate)
        eto_from_api = day_data.get("eto_fao_mm_day")
        if eto_from_api is not None:
            eto = float(eto_from_api)
        else:
            # Fall back to manual Penman-Monteith calculation
            temp_max = day_data.get("temp_max_c") or 30.0
            temp_min = day_data.get("temp_min_c") or 20.0
            solar_rad = day_data.get("solar_radiation_mj_m2") or 15.0
            wind_speed = (day_data.get("windspeed_max_kmh") or 10.0) / 3.6  # km/h → m/s

            eto = compute_eto_penman_monteith(
                temp_max_c=temp_max,
                temp_min_c=temp_min,
                solar_radiation_mj_m2=solar_rad,
                wind_speed_ms=wind_speed,
                humidity_percent=humidity_percent,
                elevation_m=elevation_m,
            )

        etc = eto * kc  # Crop evapotranspiration (ETc = ETo × Kc)
        precipitation = float(day_data.get("precipitation_mm") or 0.0)

        # Net irrigation requirement = ETc - Effective precipitation
        # Effective precipitation = 80% of precipitation (account for surface runoff)
        effective_rain = precipitation * 0.8
        net_irrigation = max(0.0, etc - effective_rain)

        schedule.append({
            "schedule_date": schedule_date,
            "eto_mm_day": round(eto, 2),
            "kc_value": round(kc, 3),
            "etc_mm_day": round(etc, 2),
            "recommended_water_mm": round(net_irrigation, 2),
            "weather_input_snapshot": day_data,
        })

    logger.debug("Irrigation schedule calculated", extra={"days": len(schedule), "crop": crop_name})
    return schedule
