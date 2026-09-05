"""
Advisory Service - Irrigation Repository
Handles persistence of irrigation schedules.
"""
from datetime import date
from uuid import UUID

from backend.services.advisory_service.src.models.irrigation_schedule import IrrigationSchedule
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class IrrigationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, schedules: list[IrrigationSchedule]) -> list[IrrigationSchedule]:
        for schedule in schedules:
            self.session.add(schedule)
        await self.session.flush()
        return schedules

    async def list_by_plot(
        self, plot_id: UUID, from_date: date | None = None
    ) -> list[IrrigationSchedule]:
        stmt = select(IrrigationSchedule).where(IrrigationSchedule.plot_id == plot_id)
        if from_date:
            stmt = stmt.where(IrrigationSchedule.schedule_date >= from_date)
        stmt = stmt.order_by(IrrigationSchedule.schedule_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
