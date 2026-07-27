"""
Advisory Service - Crop Recommendation Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecommendedCrop(BaseModel):
    crop_name: str
    confidence_score: Decimal = Field(..., ge=0, le=1)
    expected_yield_kg_ha: Optional[Decimal] = None
    suitability_reason: Optional[str] = None


class CropRecommendationRequest(BaseModel):
    plot_id: UUID
    season_name: str = Field("KHARIF", description="KHARIF | RABI | ZAID")
    # Optional override of soil data (for what-if scenarios)
    soil_ph_override: Optional[Decimal] = Field(None, ge=0, le=14)
    preferred_crops: Optional[List[str]] = None


class CropRecommendationResponse(BaseModel):
    id: UUID
    plot_id: UUID
    user_id: UUID
    model_version: str
    season_name: str
    top_confidence_score: Optional[Decimal] = None
    recommendations: List[RecommendedCrop]
    input_features: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
