"""
Feature Store - Schema and Entity Definitions
Provides metadata schemas for entities and feature views to ensure
consistency between training and inference data pipelines.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PLOT = "plot"
    MARKET = "market"
    DEVICE = "device"


class DataType(str, Enum):
    FLOAT = "FLOAT"
    INT = "INT"
    STRING = "STRING"
    TIMESTAMP = "TIMESTAMP"


class Feature(BaseModel):
    name: str
    data_type: DataType
    description: str


class Entity(BaseModel):
    name: EntityType
    join_key: str
    description: str


class FeatureView(BaseModel):
    name: str
    entity: EntityType
    features: List[Feature]
    ttl_seconds: int
    source_table: str


# Entities
PLOT_ENTITY = Entity(
    name=EntityType.PLOT,
    join_key="plot_id",
    description="Agricultural farm plot identifier"
)

MARKET_ENTITY = Entity(
    name=EntityType.MARKET,
    join_key="market_id",
    description="Market yard identifier"
)

DEVICE_ENTITY = Entity(
    name=EntityType.DEVICE,
    join_key="device_id",
    description="IoT sensor device identifier"
)

# Feature Views
SOIL_FEATURE_VIEW = FeatureView(
    name="soil_features",
    entity=EntityType.PLOT,
    ttl_seconds=31536000,  # 1 year TTL (soil changes slowly)
    source_table="soil_profiles",
    features=[
        Feature(name="ph_level", data_type=DataType.FLOAT, description="Soil pH level"),
        Feature(name="organic_carbon_percent", data_type=DataType.FLOAT, description="Organic Carbon percentage"),
        Feature(name="nitrogen_content", data_type=DataType.FLOAT, description="Nitrogen content (N) in kg/ha"),
        Feature(name="phosphorus_content", data_type=DataType.FLOAT, description="Phosphorus content (P) in kg/ha"),
        Feature(name="potassium_content", data_type=DataType.FLOAT, description="Potassium content (K) in kg/ha"),
        Feature(name="electrical_conductivity", data_type=DataType.FLOAT, description="Soil electrical conductivity"),
    ]
)

WEATHER_FEATURE_VIEW = FeatureView(
    name="weather_features",
    entity=EntityType.PLOT,
    ttl_seconds=2592000,  # 30 days TTL (moving window)
    source_table="weather_forecasts",
    features=[
        Feature(name="temp_max_c", data_type=DataType.FLOAT, description="Maximum daily temperature in Celsius"),
        Feature(name="temp_min_c", data_type=DataType.FLOAT, description="Minimum daily temperature in Celsius"),
        Feature(name="avg_temp_c", data_type=DataType.FLOAT, description="Average daily temperature in Celsius"),
        Feature(name="precipitation_mm", data_type=DataType.FLOAT, description="Total daily precipitation in mm"),
        Feature(name="windspeed_max_kmh", data_type=DataType.FLOAT, description="Maximum windspeed in km/h"),
        Feature(name="solar_radiation_mj_m2", data_type=DataType.FLOAT, description="Shortwave solar radiation in MJ/m2"),
        Feature(name="eto_fao_mm_day", data_type=DataType.FLOAT, description="Pre-calculated FAO-56 Reference Evapotranspiration"),
    ]
)

MARKET_FEATURE_VIEW = FeatureView(
    name="market_features",
    entity=EntityType.MARKET,
    ttl_seconds=604800,  # 7 days TTL for price inputs
    source_table="market_prices",
    features=[
        Feature(name="crop_name", data_type=DataType.STRING, description="Name of the crop"),
        Feature(name="modal_price_per_quintal", data_type=DataType.FLOAT, description="Modal price per quintal"),
        Feature(name="min_price_per_quintal", data_type=DataType.FLOAT, description="Minimum price per quintal"),
        Feature(name="max_price_per_quintal", data_type=DataType.FLOAT, description="Maximum price per quintal"),
        Feature(name="price_trend", data_type=DataType.FLOAT, description="Price momentum coefficient (7-day trend)"),
    ]
)

DEVICE_FEATURE_VIEW = FeatureView(
    name="device_features",
    entity=EntityType.DEVICE,
    ttl_seconds=86400,  # 24 hours TTL for real-time sensor streams
    source_table="iot_device_telemetry",
    features=[
        Feature(name="ambient_temp_c", data_type=DataType.FLOAT, description="Air temperature around plot in Celsius"),
        Feature(name="relative_humidity", data_type=DataType.FLOAT, description="Relative atmospheric humidity percent"),
        Feature(name="soil_moisture_vwc", data_type=DataType.FLOAT, description="Soil volumetric water content percent"),
        Feature(name="solar_lux", data_type=DataType.FLOAT, description="Light intensity in lux"),
    ]
)


class FeatureRegistry:
    """Central catalog helper for feature schemas."""

    def __init__(self) -> None:
        self.views = {
            SOIL_FEATURE_VIEW.name: SOIL_FEATURE_VIEW,
            WEATHER_FEATURE_VIEW.name: WEATHER_FEATURE_VIEW,
            MARKET_FEATURE_VIEW.name: MARKET_FEATURE_VIEW,
            DEVICE_FEATURE_VIEW.name: DEVICE_FEATURE_VIEW
        }
        self.entities = {
            EntityType.PLOT: PLOT_ENTITY,
            EntityType.MARKET: MARKET_ENTITY,
            EntityType.DEVICE: DEVICE_ENTITY
        }

    def get_view(self, name: str) -> Optional[FeatureView]:
        return self.views.get(name)

    def get_features_for_view(self, view_name: str) -> List[str]:
        view = self.get_view(view_name)
        if not view:
            return []
        return [f.name for f in view.features]
