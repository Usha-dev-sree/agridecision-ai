"""
Feature Store - Validation and Expectations
Validates feature data bounds, types, and constraints to prevent
data drift and ingestion of corrupted data points.
"""
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class ValidationReport:
    def __init__(self, view_name: str) -> None:
        self.view_name = view_name
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str) -> None:
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "view_name": self.view_name,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class FeatureValidator:
    """Validator class to run data quality checks on incoming datasets."""

    @staticmethod
    def validate_soil_features(data: Dict[str, Any]) -> ValidationReport:
        report = ValidationReport("soil_features")

        # 1. Check pH Level
        ph = data.get("ph_level")
        if ph is not None:
            if not (3.5 <= ph <= 10.0):
                report.add_error(f"Soil pH level {ph} is out of realistic physical range [3.5, 10.0]")
            if not (5.5 <= ph <= 8.0):
                report.add_warning(f"Soil pH level {ph} is outside optimal agricultural range [5.5, 8.0]")
        else:
            report.add_error("Required feature 'ph_level' is missing")

        # 2. Check Macronutrients (N, P, K)
        for nutrient, range_max in [("nitrogen_content", 1000.0), ("phosphorus_content", 500.0), ("potassium_content", 1000.0)]:
            val = data.get(nutrient)
            if val is not None:
                if val < 0.0:
                    report.add_error(f"Soil macronutrient {nutrient} value {val} cannot be negative")
                elif val > range_max:
                    report.add_warning(f"Soil macronutrient {nutrient} value {val} is exceptionally high (> {range_max})")
            else:
                report.add_warning(f"Macronutrient '{nutrient}' is missing; fallback defaults will be applied")

        # 3. Organic Carbon
        oc = data.get("organic_carbon_percent")
        if oc is not None:
            if not (0.0 <= oc <= 10.0):
                report.add_error(f"Soil Organic Carbon percentage {oc} must be in range [0.0, 10.0]")

        return report

    @staticmethod
    def validate_weather_features(data: Dict[str, Any]) -> ValidationReport:
        report = ValidationReport("weather_features")

        # Temperature checks
        tmax = data.get("temp_max_c")
        tmin = data.get("temp_min_c")
        tavg = data.get("avg_temp_c")

        if tmax is not None and tmin is not None:
            if tmin > tmax:
                report.add_error(f"Temperature inconsistency: min temp ({tmin}°C) is higher than max temp ({tmax}°C)")
            if tmax > 60.0 or tmin < -20.0:
                report.add_error(f"Temperature bounds violated: max/min values ({tmax}/{tmin}) exceed physical thresholds")
        
        if tavg is not None:
            if not (-20.0 <= tavg <= 60.0):
                report.add_error(f"Average temperature {tavg}°C is outside valid range [-20, 60]")

        # Precipitation check
        precip = data.get("precipitation_mm")
        if precip is not None:
            if precip < 0.0:
                report.add_error(f"Precipitation {precip} mm cannot be negative")
            if precip > 500.0:
                report.add_warning(f"Extreme precipitation event detected: {precip} mm in a single day")

        return report

    @staticmethod
    def validate_market_features(data: Dict[str, Any]) -> ValidationReport:
        report = ValidationReport("market_features")

        modal = data.get("modal_price_per_quintal")
        min_p = data.get("min_price_per_quintal")
        max_p = data.get("max_price_per_quintal")

        if modal is not None and min_p is not None and max_p is not None:
            if min_p < 0 or modal < 0 or max_p < 0:
                report.add_error("Market prices cannot be negative values")
            if not (min_p <= modal <= max_p):
                report.add_error(f"Market price inconsistency: modal price ({modal}) must sit between min ({min_p}) and max ({max_p})")
        else:
            report.add_error("Pricing structure requires modal, min, and max price fields")

        return report

    @staticmethod
    def validate_device_features(data: Dict[str, Any]) -> ValidationReport:
        report = ValidationReport("device_features")

        moisture = data.get("soil_moisture_vwc")
        if moisture is not None:
            if not (0.0 <= moisture <= 100.0):
                report.add_error(f"Volumetric Water Content {moisture}% must be in bounds [0, 100]")

        humidity = data.get("relative_humidity")
        if humidity is not None:
            if not (0.0 <= humidity <= 100.0):
                report.add_error(f"Relative humidity {humidity}% must be in bounds [0, 100]")

        return report
