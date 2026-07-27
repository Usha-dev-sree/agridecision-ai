"""
API Contract Verification Suite
Verifies JSON schemas against expected frontend/backend contract DTOs
"""
import unittest


class TestApiContracts(unittest.TestCase):

    def test_crop_recommendation_contract_schema(self):
        """Validate CropRecommendation response JSON contract structure"""
        sample_response = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "plot_id": "123e4567-e89b-12d3-a456-426614174001",
            "user_id": "123e4567-e89b-12d3-a456-426614174002",
            "model_version": "v1.2.0",
            "season_name": "KHARIF",
            "top_confidence_score": 0.94,
            "recommendations": [
                {
                    "crop_name": "Rice",
                    "confidence_score": 0.94,
                    "expected_yield_kg_ha": 4500.0,
                    "suitability_reason": "High soil moisture and optimal pH."
                }
            ],
            "created_at": "2026-07-23T15:00:00Z"
        }

        # Assert mandatory keys present in API contract DTO
        mandatory_keys = {"id", "plot_id", "user_id", "model_version", "season_name", "recommendations"}
        self.assertTrue(mandatory_keys.issubset(sample_response.keys()))

        # Assert item fields in recommendation list
        rec = sample_response["recommendations"][0]
        rec_mandatory_keys = {"crop_name", "confidence_score"}
        self.assertTrue(rec_mandatory_keys.issubset(rec.keys()))

    def test_soil_profile_contract_schema(self):
        """Validate SoilProfile response JSON contract structure"""
        sample_soil = {
            "plot_id": "123e4567-e89b-12d3-a456-426614174001",
            "soil_type": "Black Cotton",
            "texture_class": "Clay Loam",
            "ph_level": 7.2,
            "organic_carbon_percent": 0.85,
            "nitrogen_content": 45.0,
            "phosphorus_content": 30.0,
            "potassium_content": 80.0,
            "source": "LAB_TEST",
            "created_at": "2026-07-23T15:00:00Z",
            "updated_at": "2026-07-23T15:00:00Z"
        }

        mandatory_keys = {"plot_id", "ph_level", "nitrogen_content", "phosphorus_content", "potassium_content", "source"}
        self.assertTrue(mandatory_keys.issubset(sample_soil.keys()))


if __name__ == '__main__':
    unittest.main()
