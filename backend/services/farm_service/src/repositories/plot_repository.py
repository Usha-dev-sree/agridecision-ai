"""
Farm Service - Plot Repository
Handles database operations for farm.farm_plot and farm.plot_boundary.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.farm_service.src.models.farm_plot import FarmPlot
from backend.services.farm_service.src.models.plot_boundary import PlotBoundary
from backend.services.farm_service.src.schemas.plots import PlotCreate, PlotUpdate


class PlotRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, plot_id: UUID) -> Optional[FarmPlot]:
        stmt = select(FarmPlot).where(FarmPlot.id == plot_id).options(selectinload(FarmPlot.boundary))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: UUID) -> List[FarmPlot]:
        stmt = select(FarmPlot).where(
            FarmPlot.owner_id == owner_id,
            FarmPlot.is_active == True
        ).options(selectinload(FarmPlot.boundary))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_plot(self, owner_id: UUID, data: PlotCreate) -> FarmPlot:
        # Initial creation without boundary (area = 0 until boundary is set)
        plot = FarmPlot(
            owner_id=owner_id,
            name=data.name,
            total_area_ha=0.0,
            irrigation_type=data.irrigation_type,
            is_active=True
        )
        self.session.add(plot)
        await self.session.flush()
        return plot

    async def update_plot(self, plot: FarmPlot, data: PlotUpdate) -> FarmPlot:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plot, key, value)
        await self.session.flush()
        return plot

    async def delete_plot(self, plot: FarmPlot) -> None:
        plot.is_active = False
        await self.session.flush()

    async def upsert_boundary(self, plot_id: UUID, wkt_geom: str, geojson_str: str, area_ha: float, centroid: tuple[float, float]) -> PlotBoundary:
        """Upsert the geometric boundary for a plot using Well-Known Text (WKT)."""
        stmt = select(PlotBoundary).where(PlotBoundary.plot_id == plot_id)
        result = await self.session.execute(stmt)
        boundary = result.scalar_one_or_none()

        if boundary:
            # For GeoAlchemy2 updates, use ST_GeomFromText with SRID 4326
            boundary.geom = f"SRID=4326;{wkt_geom}"
            boundary.original_geojson = geojson_str
        else:
            boundary = PlotBoundary(
                plot_id=plot_id,
                geom=f"SRID=4326;{wkt_geom}",
                original_geojson=geojson_str
            )
            self.session.add(boundary)

        # Update the plot's calculated fields
        plot_stmt = select(FarmPlot).where(FarmPlot.id == plot_id)
        plot_result = await self.session.execute(plot_stmt)
        plot = plot_result.scalar_one()
        plot.total_area_ha = area_ha
        plot.centroid_lng = centroid[0]
        plot.centroid_lat = centroid[1]

        await self.session.flush()
        return boundary
