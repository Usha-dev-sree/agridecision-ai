"""
Farm Service - Boundaries Router
Endpoints for uploading and modifying plot boundaries (GeoJSON).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.plots import BoundaryResponse, GeoJSONFeature
from backend.services.farm_service.src.services.boundary_service import BoundaryService

router = APIRouter(prefix="/v1/plots/{plot_id}/boundary", tags=["Boundaries"])


def get_boundary_service(session: AsyncSession = Depends(get_db)) -> BoundaryService:
    repo = PlotRepository(session)
    return BoundaryService(repo)


@router.put("", response_model=BoundaryResponse, status_code=status.HTTP_200_OK)
async def update_boundary(
    plot_id: UUID,
    geojson_feature: GeoJSONFeature,
    current_user: dict = Depends(get_current_user),
    boundary_service: BoundaryService = Depends(get_boundary_service)
):
    """
    Upload or replace the physical boundaries of a farm plot using GeoJSON.
    Calculates the exact area in Hectares and the centroid.
    """
    owner_id = UUID(current_user["sub"])
    return await boundary_service.update_boundary(plot_id, owner_id, geojson_feature)
