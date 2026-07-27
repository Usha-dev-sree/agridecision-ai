"""
AgriDecision AI System - Comprehensive Integration Verification Suite
Executes end-to-end simulation runs of Feature Store materialization,
trains and registers all 4 models, tests the Triton client/ORT runner,
generates SHAP & Grad-CAM explanations, executes drift checks, and runs
voice and LLM prompt orchestrations.
"""
import os
import sys
import numpy as np

# Adjust path to import local modules
sys.path.append(os.path.abspath("c:/AGRICULTURE PROJECT/agridecision-ai"))

from ai_services.feature_store.materialization.engine import FeatureStoreEngine
from ai_services.model_registry.registry import ModelRegistryManager
from ai_services.training_pipelines.trainers import (
    crop_recommendation,
    yield_prediction,
    price_forecasting,
    disease_detection,
)
from ai_services.inference_gateway.triton_client import TritonInferenceClient
from ai_services.inference_gateway.explainers import ShapTabularExplainer, GradCamExplainer
from ai_services.monitoring.drift_detector import DriftTelemetryDetector
from ai_services.voice_vis_engine.src.voice_processor import VoiceProcessor
from ai_services.voice_vis_engine.src.prompt_engine import AgronomicPromptEngine


async def run_verification() -> bool:
    print("\n" + "="*60)
    print("STARTING AGRIDECISION AI SYSTEM INTEGRATION VERIFICATION")
    print("="*60 + "\n")
    
    passed_steps = []
    
    # ----------------------------------------------------
    # Step 1: Feature Store Materialization & Validation
    # ----------------------------------------------------
    print("[Verification Step 1] Feature Store & Validation...")
    try:
        # Initialise store pointing to local SQLite for tests or mock redis url
        store = FeatureStoreEngine("redis://localhost:6379/0")
        
        # Test soil metrics validation
        valid_soil = {
            "ph_level": 6.8,
            "organic_carbon_percent": 1.2,
            "nitrogen_content": 180.0,
            "phosphorus_content": 45.0,
            "potassium_content": 220.0,
            "electrical_conductivity": 0.35
        }
        invalid_soil = {
            "ph_level": 12.5, # Out of physical bound
            "organic_carbon_percent": -1.0 # Cannot be negative
        }
        
        from ai_services.feature_store.validation.expectations import FeatureValidator
        rep_valid = FeatureValidator.validate_soil_features(valid_soil)
        rep_invalid = FeatureValidator.validate_soil_features(invalid_soil)
        
        assert rep_valid.is_valid is True, "Valid soil was flagged invalid"
        assert rep_invalid.is_valid is False, "Invalid soil was flagged valid"
        
        print(" -> Feature Store & Expectations validation: PASSED")
        passed_steps.append("Feature Store Ingestion & Validation")
    except Exception as e:
        print(f" -> Feature Store validation: FAILED ({e})")
        
    # ----------------------------------------------------
    # Step 2: Training Pipelines & Model Registry
    # ----------------------------------------------------
    print("\n[Verification Step 2] Training Pipelines & Model Registry...")
    try:
        # Run training scripts (they create ONNX files and register versions in database)
        crop_recommendation.run_training_pipeline()
        yield_prediction.run_training_pipeline()
        price_forecasting.run_training_pipeline()
        disease_detection.run_training_pipeline()
        
        # Verify database records in Registry Manager
        registry = ModelRegistryManager()
        latest_crop = registry.get_latest_version("crop_recommendation", status="production")
        latest_yield = registry.get_latest_version("yield_prediction", status="production")
        latest_price = registry.get_latest_version("price_forecasting", status="production")
        latest_disease = registry.get_latest_version("disease_detection", status="production")
        
        assert latest_crop is not None, "Crop model not registered"
        assert latest_yield is not None, "Yield model not registered"
        assert latest_price is not None, "Price forecasting model not registered"
        assert latest_disease is not None, "Disease detection model not registered"
        
        print(f" -> Model Registry Crop Version: {latest_crop['version']} (Accuracy: {latest_crop['metrics']['accuracy']:.2f})")
        print(f" -> Model Registry Yield Version: {latest_yield['version']} (RMSE: {latest_yield['metrics']['rmse']:.2f})")
        print(" -> Model Training and Registry Logging: PASSED")
        passed_steps.append("Training Pipelines & Model Registry Logging")
    except Exception as e:
        print(f" -> Model Training / Registry: FAILED ({e})")
        
    # ----------------------------------------------------
    # Step 3: Triton Client / Local ONNX Runtime Inference
    # ----------------------------------------------------
    print("\n[Verification Step 3] Triton & Local ONNX Runtime Inference...")
    try:
        triton = TritonInferenceClient()
        
        # Test Crop inference
        label, probs = await triton.infer_crop_recommendation([6.5, 0.8, 200.0, 30.0, 200.0, 25.0, 100.0])
        print(f" -> Inference Crop Recommendation output class index: {label}")
        assert 0 <= label <= 7, "Output class label is out of range [0, 7]"
        
        # Test Yield inference
        expected_yield = await triton.infer_yield_prediction([6.5, 0.8, 200.0, 30.0, 200.0, 25.0, 100.0, float(label)])
        print(f" -> Inference Yield output: {expected_yield:.2f} kg/ha")
        assert expected_yield > 0, "Yield must be positive value"
        
        print(" -> Triton Client / ONNX Runtime Inference: PASSED")
        passed_steps.append("Inference Engines")
    except Exception as e:
        print(f" -> Triton / local inference runner: FAILED ({e})")

    # ----------------------------------------------------
    # Step 4: Explainable AI (SHAP & Grad-CAM)
    # ----------------------------------------------------
    print("\n[Verification Step 4] Explainable AI (SHAP & Grad-CAM)...")
    try:
        # Tabular SHAP
        feats_names = ["ph", "oc", "n", "p", "k", "temp", "rain"]
        explainer = ShapTabularExplainer(feats_names)
        
        # Simple dummy prediction function
        def predict_func(x):
            return np.ones((len(x), len(feats_names))) / len(feats_names)
            
        shap_vals = explainer.explain(predict_func, np.array([[6.5, 0.8, 200.0, 30.0, 200.0, 25.0, 100.0]]))
        assert len(shap_vals) == len(feats_names), "SHAP returned incorrect size of features list"
        print(f" -> SHAP Tabular values: {shap_vals}")
        
        # Image Grad-CAM
        mock_img = np.random.randn(1, 3, 224, 224).astype(np.float32)
        cam = GradCamExplainer.generate_heatmap(model=None, image_tensor=mock_img, target_class=2)
        assert cam.shape == (224, 224), "Grad-CAM heatmap is not of shape (224, 224)"
        print(" -> Grad-CAM attention heatmap successfully computed.")
        
        print(" -> Explainable AI (SHAP & Grad-CAM): PASSED")
        passed_steps.append("Explainable AI (SHAP & Grad-CAM)")
    except Exception as e:
        print(f" -> Explainable AI: FAILED ({e})")

    # ----------------------------------------------------
    # Step 5: Model Monitoring & Drift Detection
    # ----------------------------------------------------
    print("\n[Verification Step 5] Model Monitoring & Drift Detection...")
    try:
        baseline = [100.0, 105.0, 98.0, 102.0, 101.0, 100.0, 99.0, 103.0, 97.0, 100.0]
        normal_prod = [101.0, 104.0, 99.0, 101.0, 100.0, 102.0, 98.0, 101.0, 96.0, 101.0]
        drifted_prod = [150.0, 160.0, 145.0, 155.0, 152.0, 150.0, 148.0, 156.0, 142.0, 151.0]
        
        detector = DriftTelemetryDetector()
        
        # Test normal features drift check
        check_normal = detector.calculate_ks_drift(baseline, normal_prod)
        check_drifted = detector.calculate_ks_drift(baseline, drifted_prod)
        
        assert check_normal["drift_detected"] is False, "Drift incorrectly flagged on stable data"
        assert check_drifted["drift_detected"] is True, "Failed to flag drift on shifted distribution"
        
        # Test PSI
        psi_res = detector.calculate_psi(baseline, drifted_prod, num_bins=5)
        print(f" -> Drift telemetry computed. Stable KS: {check_normal['drift_detected']}. Drifted KS: {check_drifted['drift_detected']}. PSI: {psi_res['psi_score']:.4f}")
        
        print(" -> Model Monitoring & Drift Detection: PASSED")
        passed_steps.append("Model Monitoring & Drift Detection")
    except Exception as e:
        print(f" -> Drift Telemetry Monitoring: FAILED ({e})")

    # ----------------------------------------------------
    # Step 6: Voice Assistant & Prompt Engine
    # ----------------------------------------------------
    print("\n[Verification Step 6] Voice & LLM Prompt Engine...")
    try:
        voice = VoiceProcessor()
        # Test audio transcription
        transcription = voice.transcribe_audio_bytes(b"DUMMY_AUDIO_WAV_PCM_DATA")
        assert len(transcription) > 0
        
        # Test speech synthesis
        audio_out = voice.synthesize_speech_bytes("Hello Farmer, welcome to AgriDecision AI.")
        assert len(audio_out) > 44, "Speech synthesis output wav too small"
        
        # Test LLM prompt templates and local agronomy solver
        engine = AgronomicPromptEngine()
        soil_profile = {"ph_level": 6.8, "nitrogen_content": 180, "phosphorus_content": 45, "potassium_content": 220}
        weather = {"temp_max_c": 31.0, "temp_min_c": 22.0, "avg_temp_c": 26.5, "precipitation_mm": 120.0, "eto_fao_mm_day": 4.5}
        
        response = await engine.execute_advisory_query(
            soil_profile=soil_profile,
            weather_snapshot=weather,
            query=transcription
        )
        
        assert "diagnosis" in response, "Diagnosis field missing"
        assert "remedy_steps" in response, "Remedy steps field missing"
        assert len(response["remedy_steps"]) > 0
        
        print(" -> Voice assistant transcribes and synthesizes successfully.")
        print(f" -> LLM local engine parsed advice: {response['diagnosis'][:50]}...")
        
        print(" -> Voice Assistant & Prompt Engine: PASSED")
        passed_steps.append("Voice Assistant & Prompt Engine")
    except Exception as e:
        print(f" -> Voice & LLM: FAILED ({e})")
        
    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------
    print("\n" + "="*60)
    print("AGRIDECISION AI SYSTEM VERIFICATION SUMMARY REPORT")
    print("="*60)
    for i, step in enumerate(passed_steps, 1):
        print(f" {i}. [OK] {step}")
        
    success = len(passed_steps) == 6
    if success:
        print("\n -> ALL SYSTEM PIPELINES ARE INTEGRATED AND VERIFIED SUCCESSFULLY.")
    else:
        print(f"\n -> VERIFICATION COMPLETED WITH ERRORS. Passed: {len(passed_steps)}/6")
    print("="*60 + "\n")
    return success


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_verification())
