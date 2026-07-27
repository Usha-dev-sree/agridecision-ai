"""
Advisory Service - Irrigation Service (Business Logic)
Fetches weather data, runs Penman-Monteith, and persists schedule records.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from backend.common.logging import get_logger
from backend.services.advisory_service.src.clients.farm_client import FarmServiceClient
from backend.services.advisory_service.src.clients.weather_client import WeatherClient
from backend.services.advisory_service.src.engines.irrigation_engine import calculate_irrigation_schedule
from backend.services.advisory_service.src.models.irrigation_schedule import IrrigationSchedule
from backend.services.advisory_service.src.repositories.irrigation_repository import IrrigationRepository
from backend.services.advisory_service.src.schemas.irrigation import (
    DailyIrrigationEntry,
    IrrigationRequest,
    IrrigationScheduleResponse,
)

logger = get_logger(__name__)


class IrrigationService:
    def __init__(
        self,
        repo: IrrigationRepository,
        farm_client: FarmServiceClient,
        weather_client: WeatherClient,
    ):
        self.repo = repo
        self.farm_client = farm_client
        self.weather_client = weather_client

    async def generate_schedule(
        self, user_id: UUID, request: IrrigationRequest, access_token: str, crop_name: Optional[str] = None
    ) -> IrrigationScheduleResponse:
        """Fetch weather forecast, run irrigation engine, persist results."""
        plot_id = request.plot_id

        # 1. Get plot centroid from Farm Service
        plot_data = await self.farm_client.get_plot(plot_id, access_token)
        centroid_lat = plot_data.get("centroid_lat")
        centroid_lng = plot_data.get("centroid_lng")

        if not centroid_lat or not centroid_lng:
            # Use a default fallback location (center of India) if centroid is missing
            centroid_lat, centroid_lng = 20.5937, 78.9629
            logger.warning("Plot centroid missing; using India default", extra={"plot_id": str(plot_id)})

        # 2. Fetch weather forecast
        weather_data = await self.weather_client.get_forecast(
            lat=float(centroid_lat),
            lon=float(centroid_lng),
            forecast_days=request.forecast_days,
        )

        # 3. Run irrigation engine (Penman-Monteith)
        schedule_data = calculate_irrigation_schedule(
            weather_forecast=weather_data,
            crop_name=crop_name,
        )

        # 4. Persist schedule rows to DB
        db_schedules = [
            IrrigationSchedule(
                plot_id=plot_id,
                user_id=user_id,
                crop_season_id=request.crop_season_id,
                schedule_date=entry["schedule_date"],
                eto_mm_day=entry["eto_mm_day"],
                kc_value=entry["kc_value"],
                etc_mm_day=entry["etc_mm_day"],
                recommended_water_mm=entry["recommended_water_mm"],
                weather_input_snapshot=entry["weather_input_snapshot"],
            )
            for entry in schedule_data
        ]
        await self.repo.bulk_create(db_schedules)

        # 5. Build response
        entries = [
            DailyIrrigationEntry(
                schedule_date=entry["schedule_date"],
                eto_mm_day=entry["eto_mm_day"],
                kc_value=entry["kc_value"],
                etc_mm_day=entry["etc_mm_day"],
                recommended_water_mm=entry["recommended_water_mm"],
            )
            for entry in schedule_data
        ]

        logger.info(
            "Irrigation schedule generated",
            extra={"plot_id": str(plot_id), "days": len(entries), "crop": crop_name}
        )

        return IrrigationScheduleResponse(
            plot_id=plot_id,
            user_id=user_id,
            crop_season_id=request.crop_season_id,
            schedule=entries,
        )

    async def get_schedule(
        self, plot_id: UUID, user_id: UUID, from_date: Optional[date] = None
    ) -> List[IrrigationSchedule]:
        return await self.repo.list_by_plot(plot_id, from_date)
