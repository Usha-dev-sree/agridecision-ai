"""
Analytics Service - Core Analytics Aggregation Service
Provides farm-level and regional analytics with PostgreSQL queries and Redis caching.
"""
import json
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.logging import get_logger
from backend.services.analytics_service.src.schemas.analytics import (
    PlotAnalyticsResponse,
    RegionalAnalyticsResponse,
)

logger = get_logger(__name__)

CACHE_TTL = 600  # 10 minutes


class AnalyticsService:
    """Analytics aggregation engine backed by PostgreSQL + Redis cache."""

    def __init__(self, db: AsyncSession, redis: Redis | None = None):
        self._db = db
        self._redis = redis

    # ── Plot-Level Analytics ───────────────────────────────────────────────────

    async def get_plot_analytics(self, plot_id: str) -> PlotAnalyticsResponse:
        """Calculate aggregated soil, irrigation, and yield metrics for a plot."""
        cache_key = f"analytics:plot:{plot_id}"

        # Check Redis cache
        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                return PlotAnalyticsResponse(**json.loads(cached))

        # Query plot metadata
        plot_result = await self._db.execute(
            text("SELECT area_hectares FROM farm_plots WHERE id = :plot_id"),
            {"plot_id": plot_id},
        )
        plot_row = plot_result.fetchone()
        total_area = plot_row.area_hectares if plot_row else 0.0

        # Aggregate soil health score (average of N, P, K, pH, organic carbon metrics)
        soil_result = await self._db.execute(
            text("""
                SELECT COALESCE(AVG(health_score), 0.0) AS avg_score
                FROM soil_analyses
                WHERE plot_id = :plot_id
                ORDER BY analysis_date DESC
                LIMIT 10
            """),
            {"plot_id": plot_id},
        )
        soil_row = soil_result.fetchone()
        soil_health_score = round(float(soil_row.avg_score) if soil_row else 0.0, 1)

        # Compute irrigation efficiency from sensor data
        irrigation_result = await self._db.execute(
            text("""
                SELECT
                    CASE WHEN SUM(water_applied_liters) > 0
                        THEN (SUM(water_utilized_liters) / SUM(water_applied_liters)) * 100
                        ELSE 0
                    END AS efficiency
                FROM irrigation_logs
                WHERE plot_id = :plot_id
                  AND log_date >= CURRENT_DATE - INTERVAL '90 days'
            """),
            {"plot_id": plot_id},
        )
        irr_row = irrigation_result.fetchone()
        irrigation_efficiency = round(float(irr_row.efficiency) if irr_row else 0.0, 1)

        # Historical yield data
        yield_result = await self._db.execute(
            text("""
                SELECT harvest_year, yield_kg_per_hectare
                FROM yield_records
                WHERE plot_id = :plot_id
                ORDER BY harvest_year DESC
                LIMIT 5
            """),
            {"plot_id": plot_id},
        )
        yield_history: list[dict[str, Any]] = [
            {"year": row.harvest_year, "yield_kg_ha": float(row.yield_kg_per_hectare)}
            for row in yield_result.fetchall()
        ]

        # Disease incident count (last 12 months)
        disease_result = await self._db.execute(
            text("""
                SELECT COUNT(*) AS cnt
                FROM disease_detections
                WHERE plot_id = :plot_id
                  AND detected_at >= CURRENT_DATE - INTERVAL '365 days'
            """),
            {"plot_id": plot_id},
        )
        disease_count = disease_result.scalar_one()

        response = PlotAnalyticsResponse(
            plot_id=plot_id,
            total_area_ha=float(total_area),
            soil_health_score=soil_health_score,
            irrigation_efficiency_pct=irrigation_efficiency,
            yield_history=yield_history,
            disease_incidents_count=int(disease_count),
        )

        # Populate cache
        if self._redis:
            await self._redis.set(cache_key, response.model_dump_json(), ex=CACHE_TTL)

        return response

    # ── Regional Analytics ─────────────────────────────────────────────────────

    async def get_regional_analytics(self, region_name: str) -> RegionalAnalyticsResponse:
        """Calculate regional farm performance metrics from aggregated data."""
        cache_key = f"analytics:regional:{region_name}"

        # Check Redis cache
        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                return RegionalAnalyticsResponse(**json.loads(cached))

        # Total farms in region
        farms_result = await self._db.execute(
            text("SELECT COUNT(DISTINCT id) FROM farm_plots WHERE region = :region"),
            {"region": region_name},
        )
        total_farms = farms_result.scalar_one()

        # Top crops by acreage
        crops_result = await self._db.execute(
            text("""
                SELECT crop_name, 
                       ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS pct
                FROM crop_seasons
                WHERE region = :region
                GROUP BY crop_name
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """),
            {"region": region_name},
        )
        top_crops: list[dict[str, Any]] = [
            {"crop": row.crop_name, "percentage": float(row.pct)}
            for row in crops_result.fetchall()
        ]

        # Average yield
        avg_yield_result = await self._db.execute(
            text("""
                SELECT COALESCE(AVG(yr.yield_kg_per_hectare), 0.0) AS avg_yield
                FROM yield_records yr
                JOIN farm_plots fp ON yr.plot_id = fp.id
                WHERE fp.region = :region
                  AND yr.harvest_year = EXTRACT(YEAR FROM CURRENT_DATE)
            """),
            {"region": region_name},
        )
        avg_yield = round(float(avg_yield_result.scalar_one()), 1)

        # Disease outbreak risk (count of recent detections)
        outbreak_result = await self._db.execute(
            text("""
                SELECT COUNT(*) AS cnt
                FROM disease_detections dd
                JOIN farm_plots fp ON dd.plot_id = fp.id
                WHERE fp.region = :region
                  AND dd.detected_at >= CURRENT_DATE - INTERVAL '30 days'
            """),
            {"region": region_name},
        )
        outbreak_count = outbreak_result.scalar_one()

        if outbreak_count > 50:
            risk_level = "CRITICAL"
        elif outbreak_count > 20:
            risk_level = "HIGH"
        elif outbreak_count > 5:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        response = RegionalAnalyticsResponse(
            region_name=region_name,
            total_farms_count=int(total_farms),
            top_crops=top_crops,
            average_yield_kg_ha=avg_yield,
            disease_outbreak_risk=risk_level,
        )

        # Populate cache
        if self._redis:
            await self._redis.set(cache_key, response.model_dump_json(), ex=CACHE_TTL)

        return response
