"""
Market Service - FastAPI Router
"""

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.market_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.market_service.src.schemas.market import (
    MandiPricesResponse,
    MarketPriceForecastResponse,
)
from backend.services.market_service.src.services.market_service import MarketService

router = APIRouter(prefix="/v1/market", tags=["Market"])


@router.get("/prices", response_model=MandiPricesResponse)
async def get_mandi_prices(
    commodity: str | None = Query(None, description="Filter by crop/commodity name"),
    state: str | None = Query(None, description="Filter by Indian State"),
    mandi_name: str | None = Query(None, description="Filter by Mandi location"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve Mandi commodity rates with Redis caching and PostgreSQL fallback."""
    service = MarketService(db, redis)
    return await service.get_mandi_prices(commodity, state, mandi_name)


@router.get("/forecast", response_model=MarketPriceForecastResponse)
async def get_price_forecast(
    commodity: str = Query("Wheat", description="Commodity name"),
    mandi_name: str = Query("Khanna Grain Market", description="Mandi market name"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve 14-day AI commodity price trend forecast."""
    service = MarketService(db, redis)
    return await service.get_price_forecast(commodity, mandi_name)
