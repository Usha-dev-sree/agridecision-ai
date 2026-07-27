"""
Feature Store - Materialization Engine
Manages writing features to the Redis online cache (for real-time inference)
and saving/retrieving historical features (for training).
"""
import json
import logging
from typing import Any, Dict, List, Optional

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from ai_services.feature_store.features.definitions import FeatureRegistry
from ai_services.feature_store.validation.expectations import FeatureValidator

logger = logging.getLogger(__name__)


class MockRedis:
    """Mock Redis client in-memory fallback for local verification."""
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value

    async def get(self, key: str) -> Optional[str]:
        return self.store.get(key)

    async def close(self) -> None:
        pass



class FeatureStoreEngine:
    """Async engine to interact with Redis online features and validate data quality."""

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self.redis_client: Optional[Any] = None
        self.registry = FeatureRegistry()

    async def connect(self) -> None:
        """Establish connection to Redis online store."""
        if not self.redis_client:
            if aioredis:
                self.redis_client = aioredis.from_url(
                    self.redis_url, decode_responses=True, socket_timeout=5.0
                )
                logger.info("Connected to online Feature Store at Redis")
            else:
                self.redis_client = MockRedis()
                logger.warning("Redis library missing. Running Feature Store online cache with in-memory MockRedis.")

    async def close(self) -> None:
        """Close connection to Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _get_key(self, view_name: str, entity_id: str) -> str:
        return f"feature_store:{view_name}:{entity_id}"

    async def write_online_features(
        self, view_name: str, entity_id: str, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates and writes features to Redis online store.
        Returns the validation report dictionary.
        """
        await self.connect()
        assert self.redis_client is not None

        # 1. Run Data Quality Validations
        if view_name == "soil_features":
            report = FeatureValidator.validate_soil_features(features)
        elif view_name == "weather_features":
            report = FeatureValidator.validate_weather_features(features)
        elif view_name == "market_features":
            report = FeatureValidator.validate_market_features(features)
        elif view_name == "device_features":
            report = FeatureValidator.validate_device_features(features)
        else:
            raise ValueError(f"Unknown Feature View: {view_name}")

        if not report.is_valid:
            logger.error(
                "Data validation failed for Feature View %s and ID %s: %s",
                view_name, entity_id, report.errors
            )
            return report.to_dict()

        # 2. Extract declared features based on view definitions
        view_def = self.registry.get_view(view_name)
        if not view_def:
            raise ValueError(f"Feature view {view_name} not registered in schema definitions.")

        payload = {}
        for f in view_def.features:
            if f.name in features:
                payload[f.name] = features[f.name]

        # 3. Write to Redis with TTL
        key = self._get_key(view_name, entity_id)
        await self.redis_client.setex(
            key,
            view_def.ttl_seconds,
            json.dumps(payload)
        )
        logger.debug("Successfully materialized %s features to online store for %s", view_name, entity_id)
        return report.to_dict()

    async def read_online_features(self, view_name: str, entity_id: str) -> Dict[str, Any]:
        """Retrieve features from the online cache, returns empty dict if missing."""
        await self.connect()
        assert self.redis_client is not None

        key = self._get_key(view_name, entity_id)
        raw = await self.redis_client.get(key)
        if not raw:
            return {}

        return json.loads(raw)

    async def get_multi_features(
        self, entity_id: str, view_names: List[str]
    ) -> Dict[str, Any]:
        """Aggregate online features across multiple views (e.g., Soil + Weather for recommendation)."""
        combined = {}
        for view in view_names:
            feats = await self.read_online_features(view, entity_id)
            combined.update(feats)
        return combined

    async def materialize_offline_historical(
        self, view_name: str, data_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Simulate/process batch offline features for model training datasets.
        Validates historical records and filters out rows failing critical data quality constraints.
        """
        valid_records = []
        for record in data_history:
            entity_id = record.get("entity_id", "unknown")
            # Extract features from record
            if view_name == "soil_features":
                rep = FeatureValidator.validate_soil_features(record)
            elif view_name == "weather_features":
                rep = FeatureValidator.validate_weather_features(record)
            elif view_name == "market_features":
                rep = FeatureValidator.validate_market_features(record)
            elif view_name == "device_features":
                rep = FeatureValidator.validate_device_features(record)
            else:
                continue

            if rep.is_valid:
                valid_records.append(record)
            else:
                logger.warning("Historical record for entity %s failed validation, skipping.", entity_id)

        return valid_records
