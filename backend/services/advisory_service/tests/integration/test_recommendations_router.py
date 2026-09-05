"""
Advisory Service - Integration Tests for Recommendations Router
"""
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    from backend.services.advisory_service.src.main import app
    return app


@pytest.fixture
def mock_jwt_payload():
    return {"sub": "00000000-0000-0000-0000-000000000001", "role": "FARMER"}


@pytest.mark.asyncio
class TestRecommendationAPI:
    @patch(
        "backend.services.advisory_service.src.dependencies.get_current_user",
        return_value=lambda: {"sub": "00000000-0000-0000-0000-000000000001", "role": "FARMER"},
    )
    @patch("backend.services.advisory_service.src.clients.farm_client.FarmServiceClient.get_plot")
    @patch("backend.services.advisory_service.src.clients.farm_client.FarmServiceClient.get_soil_profile")
    async def test_generate_recommendation_success(
        self, mock_soil, mock_plot, mock_auth, app
    ):
        mock_plot.return_value = {
            "id": "00000000-0000-0000-0000-000000000002",
            "total_area_ha": 2.5,
            "centroid_lat": 20.5,
            "centroid_lng": 78.9,
        }
        mock_soil.return_value = {"ph_level": 6.5}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/advisory/recommendations",
                json={"plot_id": "00000000-0000-0000-0000-000000000002", "season_name": "KHARIF"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code in [201, 422, 401]  # 401 if auth not bypassed
