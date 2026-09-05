"""
Advisory Service - Crop Recommendation Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecommendedCrop(BaseModel):
    crop_name: str
    confidence_score: Decimal = Field(..., ge=0, le=1)
    expected_yield_kg_ha: Decimal | None = None
    suitability_reason: str | None = None


class CropRecommendationRequest(BaseModel):
    plot_id: UUID
    season_name: str = Field("KHARIF", description="KHARIF | RABI | ZAID")
    # Optional override of soil data (for what-if scenarios)
    soil_ph_override: Decimal | None = Field(None, ge=0, le=14)
    preferred_crops: list[str] | None = None


class CropRecommendationResponse(BaseModel):
    id: UUID
    plot_id: UUID
    user_id: UUID
    model_version: str
    season_name: str
    top_confidence_score: Decimal | None = None
    recommendations: list[RecommendedCrop]
    input_features: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
