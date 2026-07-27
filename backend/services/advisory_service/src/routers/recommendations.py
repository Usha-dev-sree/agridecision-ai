"""
Advisory Service - Recommendations Router
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.advisory_service.src.clients.farm_client import FarmServiceClient
from backend.services.advisory_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.advisory_service.src.repositories.recommendation_repository import RecommendationRepository
from backend.services.advisory_service.src.schemas.recommendation import (
    CropRecommendationRequest,
    CropRecommendationResponse,
)
from backend.services.advisory_service.src.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/v1/advisory/recommendations", tags=["Crop Recommendations"])


def get_recommendation_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> RecommendationService:
    repo = RecommendationRepository(session)
    farm_client = FarmServiceClient()
    return RecommendationService(repo, redis, farm_client)


@router.post("", response_model=CropRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def generate_crop_recommendation(
    request: Request,
    data: CropRecommendationRequest,
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Generate AI-powered crop recommendations for a farm plot.
    Uses soil profile, seasonal context, and optional user preferences.
    """
    user_id = UUID(current_user["sub"])
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return await service.generate_recommendation(user_id, data, access_token)


@router.get("/plots/{plot_id}/history", response_model=List[CropRecommendationResponse])
async def get_recommendation_history(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """Get historical crop recommendations for a specific plot."""
    user_id = UUID(current_user["sub"])
    return await service.get_history(plot_id, user_id)
