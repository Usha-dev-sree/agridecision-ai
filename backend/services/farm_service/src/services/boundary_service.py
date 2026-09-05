"""
Farm Service - Boundary Service (Business Logic)
Handles geometric operations using Shapely and PostGIS storage.
"""
import json
from uuid import UUID

import pyproj
from backend.common.exceptions import NotFoundException, ValidationException
from backend.services.farm_service.src.repositories.plot_repository import PlotRepository
from backend.services.farm_service.src.schemas.plots import BoundaryResponse, GeoJSONFeature
from shapely.geometry import Polygon, shape
from shapely.ops import transform
from shapely.validation import make_valid


class BoundaryService:
    def __init__(self, plot_repo: PlotRepository):
        self.plot_repo = plot_repo

        # Projection from WGS84 (lon/lat) to a suitable equal-area projection
        # World Cylindrical Equal Area is good for general area calculation if local CRS isn't known
        # A more robust solution uses a dynamic UTM zone based on centroid, but this is a solid approximation
        self.project_to_area = pyproj.Transformer.from_crs(
            pyproj.CRS('EPSG:4326'),
            pyproj.CRS('EPSG:6933'),  # Equal Earth projection (meters)
            always_xy=True
        ).transform

    async def update_boundary(self, plot_id: UUID, owner_id: UUID, geojson_feature: GeoJSONFeature) -> BoundaryResponse:
        """Validate GeoJSON, calculate spatial features, and store."""
        # 1. Check ownership
        plot = await self.plot_repo.get_by_id(plot_id)
        if not plot or plot.owner_id != owner_id or not plot.is_active:
            raise NotFoundException(detail="Plot not found")

        # 2. Extract and validate geometry using Shapely
        try:
            geom_dict = geojson_feature.geometry.model_dump()
            polygon = shape(geom_dict)
        except Exception as e:
            raise ValidationException(detail="Invalid GeoJSON geometry structure", errors=[str(e)])

        if not isinstance(polygon, Polygon):
            raise ValidationException(detail="Geometry must be a single Polygon", errors=[])

        # 3. Repair polygon if self-intersecting
        if not polygon.is_valid:
            polygon = make_valid(polygon)
            # make_valid can sometimes return a MultiPolygon or GeometryCollection.
            # We strictly need a single Polygon representing the main boundary.
            if polygon.geom_type != 'Polygon':
                raise ValidationException(
                    detail="Repaired geometry is not a simple Polygon. Please fix self-intersections.",
                    errors=["Invalid topology"]
                )

        # 4. Calculate Area (in Hectares)
        # Transform the polygon from lat/lon to equal-area projection in meters
        projected_polygon = transform(self.project_to_area, polygon)
        area_sq_meters = projected_polygon.area
        area_hectares = area_sq_meters / 10000.0

        if area_hectares > 10000:
            raise ValidationException(detail="Plot area exceeds maximum allowed size (10,000 Ha)", errors=[])
        if area_hectares <= 0:
            raise ValidationException(detail="Plot area must be greater than zero", errors=[])

        # 5. Calculate Centroid
        centroid = polygon.centroid
        centroid_lng_lat = (centroid.x, centroid.y)

        # 6. Prepare WKT and raw JSON
        wkt_geom = polygon.wkt
        raw_json_str = json.dumps(geojson_feature.model_dump())

        # 7. Persist to DB via repository
        boundary = await self.plot_repo.upsert_boundary(
            plot_id=plot_id,
            wkt_geom=wkt_geom,
            geojson_str=raw_json_str,
            area_ha=area_hectares,
            centroid=centroid_lng_lat
        )

        return BoundaryResponse(
            plot_id=plot_id,
            geojson=geojson_feature,
            created_at=boundary.created_at,
            updated_at=boundary.updated_at
        )
