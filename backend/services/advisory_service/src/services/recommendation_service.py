"""
Advisory Service - Recommendation Service (Business Logic)
Orchestrates plot data fetching, feature assembly, engine invocation, and persistence.
"""
import json
from typing import List, Optional
from uuid import UUID
import numpy as np
from redis.asyncio import Redis

from backend.common.exceptions import NotFoundException
from backend.common.logging import get_logger
from backend.services.advisory_service.src.clients.farm_client import FarmServiceClient
from backend.services.advisory_service.src.clients.weather_client import WeatherClient
from backend.services.advisory_service.src.engines.recommendation_engine import (
    apply_rule_based_recommendations,
    build_feature_vector,
)
from backend.services.advisory_service.src.models.crop_recommendation import CropRecommendation
from backend.services.advisory_service.src.repositories.recommendation_repository import (
    RecommendationRepository,
)
from backend.services.advisory_service.src.schemas.recommendation import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    RecommendedCrop,
)
from backend.services.advisory_service.src.config import settings
from ai_services.inference_gateway.triton_client import TritonInferenceClient

logger = get_logger(__name__)

ADVISORY_MODEL_VERSION = "triton-ensemble-v1.0"


class RecommendationService:
    def __init__(
        self,
        repo: RecommendationRepository,
        redis: Redis,
        farm_client: FarmServiceClient,
    ):
        self.repo = repo
        self.redis = redis
        self.farm_client = farm_client
        self.weather_client = WeatherClient()
        self.triton_client = TritonInferenceClient(triton_url=settings.TRITON_GRPC_URL)

    async def generate_recommendation(
        self,
        user_id: UUID,
        request: CropRecommendationRequest,
        access_token: str,
    ) -> CropRecommendationResponse:
        plot_id = request.plot_id
        cache_key = f"advisory:crop_rec:{plot_id}:{request.season_name}"

        # 1. Check Redis cache
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info("Cache hit for crop recommendation", extra={"plot_id": str(plot_id)})
            cached_data = json.loads(cached)
            return CropRecommendationResponse(**cached_data)

        # 2. Fetch plot and soil data from Farm Service
        plot_data = await self.farm_client.get_plot(plot_id, access_token)
        soil_data = await self.farm_client.get_soil_profile(plot_id, access_token)

        plot_area_ha = float(plot_data.get("total_area_ha", 1.0))

        # Apply soil pH override from request if provided
        if request.soil_ph_override and soil_data:
            soil_data["ph_level"] = float(request.soil_ph_override)
        elif request.soil_ph_override:
            soil_data = {"ph_level": float(request.soil_ph_override)}

        # Fetch Weather Forecast from coordinate centroid
        weather_snapshot = None
        lat = plot_data.get("centroid_lat")
        lon = plot_data.get("centroid_lng")
        if lat is not None and lon is not None:
            try:
                forecasts = await self.weather_client.get_forecast(float(lat), float(lon), forecast_days=7)
                if forecasts:
                    # Extrapolate daily readings to expected averages/totals
                    avg_temp = sum(f["temp_max_c"] + f["temp_min_c"] for f in forecasts if f["temp_max_c"] is not None) / (2 * len(forecasts))
                    monthly_rainfall = sum(f["precipitation_mm"] for f in forecasts if f["precipitation_mm"] is not None) * 4.0
                    weather_snapshot = {
                        "avg_temp_c": avg_temp,
                        "monthly_rainfall_mm": monthly_rainfall
                    }
            except Exception as e:
                logger.warning("Failed to fetch weather forecast for coordinates: %s. Using default baseline.", e)

        # 3. Build feature vector
        features = build_feature_vector(
            soil_data=soil_data,
            weather_snapshot=weather_snapshot,
            plot_area_ha=plot_area_ha,
            season_name=request.season_name,
        )

        # 4. Run Triton ML model inference with rule-based fallback
        raw_recommendations = []
        try:
            input_list = [
                features["ph_level"],
                features["organic_carbon_pct"],
                features["nitrogen"],
                features["phosphorus"],
                features["potassium"],
                features["avg_temp_c"],
                features["rainfall_mm"]
            ]
            label, probs = await self.triton_client.infer_crop_recommendation(input_list)
            
            crops_list = ["rice", "maize", "soybean", "wheat", "chickpea", "mustard", "cotton", "sugarcane"]
            predicted_crop = crops_list[label] if label < len(crops_list) else "unknown"
            confidence = probs[label]

            if confidence >= 0.5:
                # Predict yield for this crop candidate
                yield_features = input_list + [float(label)]
                expected_yield = await self.triton_client.infer_yield_prediction(yield_features)
                
                raw_recommendations.append({
                    "crop_name": predicted_crop,
                    "confidence_score": round(confidence, 3),
                    "expected_yield_kg_ha": round(expected_yield, 2),
                    "suitability_reason": f"AI model high-confidence match. pH: {features['ph_level']}, Temp: {features['avg_temp_c']}C.",
                })
                
                # Add runner ups
                sorted_indices = list(np.argsort(probs)[::-1])
                for idx in sorted_indices:
                    if idx == label or idx >= len(crops_list):
                        continue
                    r_crop = crops_list[idx]
                    r_conf = probs[idx]
                    if r_conf > 0.1:
                        raw_recommendations.append({
                            "crop_name": r_crop,
                            "confidence_score": round(r_conf, 3),
                            "expected_yield_kg_ha": None,
                            "suitability_reason": f"AI model alternative suggestion (confidence {round(r_conf, 2)})."
                        })
            else:
                logger.info("ML model confidence %.3f below 0.5. Falling back to rule engine.", confidence)
                raw_recommendations = apply_rule_based_recommendations(
                    features=features,
                    season_name=request.season_name,
                    preferred_crops=request.preferred_crops,
                )
        except Exception as e:
            logger.error("Failed to run Triton model inference: %s. Reverting to rule-based fallback.", e)
            raw_recommendations = apply_rule_based_recommendations(
                features=features,
                season_name=request.season_name,
                preferred_crops=request.preferred_crops,
            )

        top_score = raw_recommendations[0]["confidence_score"] if raw_recommendations else None

        # 5. Persist to DB
        model = CropRecommendation(
            plot_id=plot_id,
            user_id=user_id,
            model_version=ADVISORY_MODEL_VERSION,
            season_name=request.season_name,
            recommendations=raw_recommendations,
            input_features=features,
            top_confidence_score=top_score,
        )
        saved = await self.repo.create(model)

        response = CropRecommendationResponse(
            id=saved.id,
            plot_id=plot_id,
            user_id=user_id,
            model_version=ADVISORY_MODEL_VERSION,
            season_name=request.season_name,
            top_confidence_score=top_score,
            recommendations=[RecommendedCrop(**r) for r in raw_recommendations],
            input_features=features,
            created_at=saved.created_at,
        )

        # 6. Cache result
        await self.redis.setex(
            cache_key,
            settings.ADVISORY_CACHE_TTL_SECONDS,
            response.model_dump_json(),
        )

        return response

    async def get_history(self, plot_id: UUID, user_id: UUID) -> List[CropRecommendationResponse]:
        records = await self.repo.list_by_plot(plot_id)
        return [
            CropRecommendationResponse(
                id=r.id,
                plot_id=r.plot_id,
                user_id=r.user_id,
                model_version=r.model_version,
                season_name=r.season_name,
                top_confidence_score=r.top_confidence_score,
                recommendations=[RecommendedCrop(**c) for c in r.recommendations],
                input_features=r.input_features,
                created_at=r.created_at,
            )
            for r in records
        ]
