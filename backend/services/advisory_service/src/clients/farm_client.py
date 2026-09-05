"""
Advisory Service - Farm Client
Calls Farm Service gRPC endpoints to retrieve plot details and soil profiles.
In this implementation, we use an internal HTTP call for simplicity
(can be replaced with gRPC stubs when protobuf is compiled).
"""
from typing import Any
from uuid import UUID

import httpx
from backend.common.exceptions import NotFoundException
from backend.common.logging import get_logger

logger = get_logger(__name__)

# In a full Kubernetes setup, this resolves via Kubernetes DNS
FARM_SERVICE_HTTP_URL = "http://farm-service:8001"


class FarmServiceClient:
    """Internal HTTP client to Farm Service REST endpoints."""

    def __init__(self, base_url: str = FARM_SERVICE_HTTP_URL):
        self.base_url = base_url

    async def get_plot(self, plot_id: UUID, access_token: str) -> dict[str, Any]:
        """Fetch farm plot details including centroid coordinates."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.base_url}/v1/plots/{plot_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 404:
                raise NotFoundException(detail=f"Plot {plot_id} not found in Farm Service")
            response.raise_for_status()
            return response.json()

    async def get_soil_profile(self, plot_id: UUID, access_token: str) -> dict[str, Any] | None:
        """Fetch soil profile for a given plot."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.base_url}/v1/plots/{plot_id}/soil",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
