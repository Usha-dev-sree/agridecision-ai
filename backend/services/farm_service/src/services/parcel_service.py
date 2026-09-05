"""
Farm Service - Parcel Geometry Operations Service
Handles parcel split & merge spatial polygon operations.
"""
from typing import Dict, Any, List
from uuid import UUID
from shapely.geometry import Polygon, LineString, shape, mapping
from shapely.ops import split, unary_union

from backend.common.exceptions import APIException
from backend.common.logging import get_logger

logger = get_logger(__name__)


class ParcelService:
    @staticmethod
    def split_polygon(geometry_geojson: Dict[str, Any], cut_line_coords: List[List[float]]) -> List[Dict[str, Any]]:
        """Split a polygon GeoJSON by a cutting LineString into sub-parcels."""
        try:
            poly = shape(geometry_geojson)
            cut_line = LineString(cut_line_coords)
            result = split(poly, cut_line)
            
            sub_parcels = []
            for idx, geom in enumerate(result.geoms if hasattr(result, 'geoms') else [result]):
                area_ha = (geom.area * 111320 * 111320) / 10000.0  # Approx degree to ha
                sub_parcels.append({
                    "parcel_index": idx + 1,
                    "area_hectares": round(area_ha, 3),
                    "geometry": mapping(geom)
                })
            return sub_parcels
        except Exception as e:
            logger.error("Error splitting parcel geometry: %s", str(e))
            raise APIException("Failed to split parcel polygon geometry", status_code=400)

    @staticmethod
    def merge_polygons(geometries_geojson: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge adjacent polygon GeoJSONs into a unified plot parcel."""
        try:
            polys = [shape(g) for g in geometries_geojson]
            merged = unary_union(polys)
            area_ha = (merged.area * 111320 * 111320) / 10000.0
            return {
                "merged_area_hectares": round(area_ha, 3),
                "geometry": mapping(merged)
            }
        except Exception as e:
            logger.error("Error merging parcel geometries: %s", str(e))
            raise APIException("Failed to merge parcel polygon geometries", status_code=400)
