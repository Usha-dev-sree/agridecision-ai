"""
Advisory Service - Irrigation Repository
Handles persistence of irrigation schedules.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.advisory_service.src.models.irrigation_schedule import IrrigationSchedule


class IrrigationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, schedules: List[IrrigationSchedule]) -> List[IrrigationSchedule]:
        for schedule in schedules:
            self.session.add(schedule)
        await self.session.flush()
        return schedules

    async def list_by_plot(
        self, plot_id: UUID, from_date: Optional[date] = None
    ) -> List[IrrigationSchedule]:
        stmt = select(IrrigationSchedule).where(IrrigationSchedule.plot_id == plot_id)
        if from_date:
            stmt = stmt.where(IrrigationSchedule.schedule_date >= from_date)
        stmt = stmt.order_by(IrrigationSchedule.schedule_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
