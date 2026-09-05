"""
AgriDecision AI - Comprehensive Test Suite
Targeting >= 95% Automated Test Coverage across Core Business Services, AI Inferences,
Security Middlewares, Feature Store Validation, and Data Contracts.
"""
import unittest
import numpy as np
from decimal import Decimal

# Import AI & Feature Store modules
from ai_services.feature_store.validation.expectations import FeatureValidator
from ai_services.inference_gateway.fallback_rules import (
    CropRecommendationFallbackRuleEngine,
    YieldPredictionFallbackRuleEngine,
    DiseaseDetectionFallbackRuleEngine,
    PriceForecastingFallbackRuleEngine,
    compute_entropy_confidence
)
from ai_services.monitoring.drift_detector import DriftTelemetryDetector
from ai_services.voice_vis_engine.src.voice_processor import VoiceProcessor
from ai_services.voice_vis_engine.src.prompt_engine import AgronomicPromptEngine


class TestFeatureStoreValidation(unittest.TestCase):
    def test_valid_soil_features(self):
        soil = {
            "ph_level": 6.8,
            "organic_carbon_percent": 1.2,
            "nitrogen_content": 180.0,
            "phosphorus_content": 45.0,
            "potassium_content": 220.0,
            "electrical_conductivity": 0.35
        }
        res = FeatureValidator.validate_soil_features(soil)
        self.assertTrue(res.is_valid)

    def test_invalid_soil_features(self):
        invalid_soil = {
            "ph_level": 15.0, # out of bound
            "organic_carbon_percent": -0.5
        }
        res = FeatureValidator.validate_soil_features(invalid_soil)
        self.assertFalse(res.is_valid)


class TestAIFallbackRuleEngines(unittest.TestCase):
    def test_crop_recommendation_fallback(self):
        res = CropRecommendationFallbackRuleEngine.recommend(ph=6.8, rainfall_mm=150.0, season="KHARIF")
        self.assertIn("recommended_crop", res)
        self.assertTrue(res["fallback_used"])

    def test_yield_prediction_fallback(self):
        res = YieldPredictionFallbackRuleEngine.estimate_yield("rice", ph=6.8, organic_carbon=1.2, nitrogen=200.0)
        self.assertGreater(res["expected_yield_kg_ha"], 1000.0)

    def test_disease_detection_fallback(self):
        res = DiseaseDetectionFallbackRuleEngine.classify(0.5)
        self.assertEqual(res["predicted_class"], "healthy")

    def test_price_forecasting_fallback(self):
        preds = PriceForecastingFallbackRuleEngine.forecast(2000.0, 7)
        self.assertEqual(len(preds), 7)
        self.assertGreater(preds[-1], 2000.0)


class TestEntropyAndDrift(unittest.TestCase):
    def test_entropy_confidence(self):
        probs_certain = [1.0, 0.0, 0.0]
        probs_uncertain = [0.33, 0.33, 0.34]
        conf_certain = compute_entropy_confidence(probs_certain)
        conf_uncertain = compute_entropy_confidence(probs_uncertain)
        self.assertGreater(conf_certain, conf_uncertain)

    def test_ks_drift_detector(self):
        baseline = [10.0, 12.0, 11.0, 10.5, 11.5] * 10
        stable_prod = [10.2, 11.8, 11.1, 10.4, 11.6] * 10
        shifted_prod = [50.0, 52.0, 51.0, 50.5, 51.5] * 10
        detector = DriftTelemetryDetector()

        res_stable = detector.calculate_ks_drift(baseline, stable_prod)
        res_shifted = detector.calculate_ks_drift(baseline, shifted_prod)
        self.assertFalse(res_stable["drift_detected"])
        self.assertTrue(res_shifted["drift_detected"])


class TestVoiceProcessorAndPromptEngine(unittest.TestCase):
    def test_voice_transcription_and_synthesis(self):
        processor = VoiceProcessor()
        text = processor.transcribe_audio_bytes(b"DUMMY_PCM_WAV_HEADER_DATA")
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

        wav_bytes = processor.synthesize_speech_bytes("Hello Farmer")
        self.assertIsInstance(wav_bytes, bytes)
        self.assertGreater(len(wav_bytes), 40)


if __name__ == '__main__':
    unittest.main()
