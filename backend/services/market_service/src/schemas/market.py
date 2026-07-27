"""
Market Service - Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class MandiPriceItem(BaseModel):
    state: str
    district: str
    mandi_name: str
    commodity: str
    variety: Optional[str] = "Standard"
    min_price: Decimal
    max_price: Decimal
    modal_price: Decimal
    reported_date: datetime


class MandiPricesResponse(BaseModel):
    total_count: int
    prices: List[MandiPriceItem]


class PriceForecastPoint(BaseModel):
    date: str
    predicted_modal_price: Decimal
    confidence_lower_bound: Decimal
    confidence_upper_bound: Decimal
    trend: str  # BULLISH, BEARISH, STABLE


class MarketPriceForecastResponse(BaseModel):
    commodity: str
    mandi_name: str
    current_modal_price: Decimal
    forecast: List[PriceForecastPoint]
