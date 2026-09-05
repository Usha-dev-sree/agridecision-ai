"""
Farm Service - Boundaries & Satellite Router
Endpoints for uploading boundaries, Sentinel-2 parcel detection, NDVI raster calculation, and parcel split/merge.
"""
from typing import Any
from uuid import UUID

from backend.services.farm_service.src.dependencies import get_current_user, get_db
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.plots import BoundaryResponse, GeoJSONFeature
from backend.services.farm_service.src.services.boundary_service import BoundaryService
from backend.services.farm_service.src.services.parcel_service import ParcelService
from backend.services.farm_service.src.services.satellite_service import SatelliteService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/plots", tags=["Boundaries & Satellite"])


def get_boundary_service(session: AsyncSession = Depends(get_db)) -> BoundaryService:
    repo = PlotRepository(session)
    return BoundaryService(repo)


@router.put("/{plot_id}/boundary", response_model=BoundaryResponse, status_code=status.HTTP_200_OK)
async def update_boundary(
    plot_id: UUID,
    geojson_feature: GeoJSONFeature,
    current_user: dict = Depends(get_current_user),
    boundary_service: BoundaryService = Depends(get_boundary_service)
):
    """Upload or replace physical boundaries using GeoJSON."""
    owner_id = UUID(current_user["sub"])
    return await boundary_service.update_boundary(plot_id, owner_id, geojson_feature)


@router.get("/{plot_id}/ndvi", status_code=status.HTTP_200_OK)
async def get_plot_ndvi(
    plot_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve latest Sentinel-2 L2A satellite pass NDVI vegetation index telemetry."""
    sat_svc = SatelliteService()
    return await sat_svc.get_plot_ndvi_telemetry(plot_id)


@router.post("/detect-boundaries", status_code=status.HTTP_200_OK)
async def detect_field_boundaries(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    current_user: dict = Depends(get_current_user)
):
    """Auto-detect field parcel boundary polygon from Sentinel-2 satellite reflectance."""
    sat_svc = SatelliteService()
    return await sat_svc.detect_field_boundaries(latitude, longitude)


@router.post("/{plot_id}/split", status_code=status.HTTP_200_OK)
async def split_parcel(
    plot_id: UUID,
    cut_line: list[list[float]],
    current_user: dict = Depends(get_current_user),
    boundary_service: BoundaryService = Depends(get_boundary_service)
):
    """Split a farm plot polygon along a cutting LineString into sub-parcels."""
    owner_id = UUID(current_user["sub"])
    plot = await boundary_service.get_plot(plot_id, owner_id)
    sub_parcels = ParcelService.split_polygon(plot.geometry, cut_line)
    return {"plot_id": str(plot_id), "sub_parcels": sub_parcels}


@router.post("/merge", status_code=status.HTTP_200_OK)
async def merge_parcels(
    geometries: list[dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Merge adjacent polygon GeoJSONs into a unified plot parcel."""
    return ParcelService.merge_polygons(geometries)
