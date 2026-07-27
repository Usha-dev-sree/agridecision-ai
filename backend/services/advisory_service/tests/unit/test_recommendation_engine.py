"""
Advisory Service - Recommendation Engine Unit Tests
"""
import pytest
from backend.services.advisory_service.src.engines.recommendation_engine import (
    SEASON_CROPS,
    apply_rule_based_recommendations,
    build_feature_vector,
)


class TestFeatureVector:
    def test_builds_with_soil_data(self):
        soil = {"ph_level": 6.8, "organic_carbon_percent": 1.2, "nitrogen_content": 180}
        features = build_feature_vector(soil, None, 2.5, "KHARIF")
        assert features["ph_level"] == 6.8
        assert features["plot_area_ha"] == 2.5

    def test_defaults_when_soil_missing(self):
        features = build_feature_vector(None, None, 1.0, "RABI")
        assert features["ph_level"] == 6.5  # Default median pH
        assert features["season"] == "RABI"


class TestRuleBasedRecommendations:
    def test_returns_recommendations(self):
        features = {"ph_level": 6.5}
        results = apply_rule_based_recommendations(features, "KHARIF")
        assert len(results) > 0

    def test_all_crops_in_correct_season(self):
        features = {"ph_level": 6.5}
        results = apply_rule_based_recommendations(features, "RABI")
        valid_crops = {c.lower() for c in SEASON_CROPS["RABI"]}
        for rec in results:
            assert rec["crop_name"] in valid_crops, f"{rec['crop_name']} not a valid RABI crop"

    def test_confidence_scores_descending(self):
        features = {"ph_level": 6.5}
        results = apply_rule_based_recommendations(features, "KHARIF")
        scores = [r["confidence_score"] for r in results]
        assert scores == sorted(scores, reverse=True), "Confidence scores must be in descending order"

    def test_preferred_crops_are_boosted(self):
        features = {"ph_level": 6.0}
        results = apply_rule_based_recommendations(features, "KHARIF", preferred_crops=["rice"])
        crop_names = [r["crop_name"] for r in results]
        assert "rice" in crop_names
