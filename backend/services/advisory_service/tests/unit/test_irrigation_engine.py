"""
Advisory Service - Irrigation Engine Unit Tests
Tests FAO-56 Penman-Monteith formula and Kc lookups.
"""
from backend.services.advisory_service.src.engines.irrigation_engine import (
    KC_TABLE,
    calculate_irrigation_schedule,
    compute_eto_penman_monteith,
    get_kc_for_crop,
)


class TestPenmanMonteith:
    def test_eto_is_positive(self):
        eto = compute_eto_penman_monteith(
            temp_max_c=32.0, temp_min_c=20.0,
            solar_radiation_mj_m2=20.0, wind_speed_ms=2.0,
            humidity_percent=60.0, elevation_m=100.0
        )
        assert eto > 0, "ETo must be positive under normal conditions"

    def test_eto_range_reasonable(self):
        """ETo in Indian conditions should be between 2–12 mm/day."""
        eto = compute_eto_penman_monteith(
            temp_max_c=35.0, temp_min_c=22.0,
            solar_radiation_mj_m2=25.0, wind_speed_ms=3.0,
            humidity_percent=50.0, elevation_m=200.0
        )
        assert 2.0 <= eto <= 12.0, f"ETo {eto} out of expected range"

    def test_eto_zero_at_extreme_conditions(self):
        """ETo should not go negative."""
        eto = compute_eto_penman_monteith(
            temp_max_c=0.0, temp_min_c=0.0,
            solar_radiation_mj_m2=0.0, wind_speed_ms=0.0,
            humidity_percent=100.0, elevation_m=0.0
        )
        assert eto >= 0.0


class TestKcLookup:
    def test_known_crop(self):
        assert get_kc_for_crop("rice") == KC_TABLE["rice"]

    def test_case_insensitive(self):
        assert get_kc_for_crop("WHEAT") == get_kc_for_crop("wheat")

    def test_unknown_crop_returns_default(self):
        assert get_kc_for_crop("unknowncrop") == KC_TABLE["default"]


class TestCalculateSchedule:
    def test_schedule_length_matches_forecast(self):
        forecast = [
            {
                "date": "2024-06-01",
                "eto_fao_mm_day": 5.0,
                "precipitation_mm": 0.0,
                "temp_max_c": 32, "temp_min_c": 22,
                "solar_radiation_mj_m2": 20, "windspeed_max_kmh": 15,
            }
            for _ in range(7)
        ]
        schedule = calculate_irrigation_schedule(forecast, crop_name="wheat")
        assert len(schedule) == 7

    def test_recommended_water_zero_when_rain_exceeds_etc(self):
        """Heavy rain should result in zero irrigation recommendation."""
        forecast = [{
            "date": "2024-06-01",
            "eto_fao_mm_day": 4.0,
            "precipitation_mm": 50.0,  # Very heavy rain
            "temp_max_c": 28, "temp_min_c": 20,
            "solar_radiation_mj_m2": 18, "windspeed_max_kmh": 10,
        }]
        schedule = calculate_irrigation_schedule(forecast, crop_name="rice")
        assert schedule[0]["recommended_water_mm"] == 0.0
