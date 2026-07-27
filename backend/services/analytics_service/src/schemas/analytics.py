"""
Analytics Service - Pydantic Schemas
"""
from typing import List, Dict
from pydantic import BaseModel


class PlotAnalyticsResponse(BaseModel):
    plot_id: str
    total_area_ha: float
    soil_health_score: float  # 0 to 100
    irrigation_efficiency_pct: float
    yield_history: List[Dict[str, float]]
    disease_incidents_count: int


class RegionalAnalyticsResponse(BaseModel):
    region_name: str
    total_farms_count: int
    top_crops: List[Dict[str, float]]
    average_yield_kg_ha: float
    disease_outbreak_risk: str  # LOW, MODERATE, HIGH, CRITICAL
