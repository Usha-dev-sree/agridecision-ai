"""
Analytics Service - FastAPI Router
"""
from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.analytics_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.analytics_service.src.schemas.analytics import (
    PlotAnalyticsResponse,
    RegionalAnalyticsResponse,
)
from backend.services.analytics_service.src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


@router.get("/plot/{plot_id}", response_model=PlotAnalyticsResponse)
async def get_plot_analytics(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve plot productivity, soil health, and historical yield metrics."""
    service = AnalyticsService(db, redis)
    return await service.get_plot_analytics(plot_id)


@router.get("/regional", response_model=RegionalAnalyticsResponse)
async def get_regional_analytics(
    region_name: str = Query("Punjab", description="Region / State name"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve regional crop performance and disease outbreak risk analysis."""
    service = AnalyticsService(db, redis)
    return await service.get_regional_analytics(region_name)
