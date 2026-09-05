"""
Training Pipeline - Yield Prediction Model
Trains an XGBoost or Scikit-Learn GradientBoostingRegressor on soil, crop,
and weather conditions to predict expected yield (kg/ha).
Evaluates performance metrics, exports to ONNX, and logs in the registry.
"""
import os
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from ai_services.model_registry.registry import ModelRegistryManager
from ai_services.training_pipelines.evaluators.metrics import ModelEvaluator
from ai_services.training_pipelines.exporters.onnx_exporter import export_sklearn_to_onnx


def generate_yield_synthetic_data(num_samples: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic soil, crop selection, and weather features for yield prediction."""
    np.random.seed(42)
    # Features:
    # 0: ph_level
    # 1: organic_carbon_percent
    # 2: nitrogen_content
    # 3: phosphorus_content
    # 4: potassium_content
    # 5: avg_temp_c
    # 6: precipitation_mm
    # 7: crop_class_id [0 to 7]
    
    ph = np.random.uniform(5.0, 9.0, num_samples)
    oc = np.random.uniform(0.2, 2.0, num_samples)
    n = np.random.uniform(60, 350, num_samples)
    p = np.random.uniform(10, 100, num_samples)
    k = np.random.uniform(60, 450, num_samples)
    temp = np.random.uniform(18, 36, num_samples)
    rain = np.random.uniform(40, 250, num_samples)
    crop_id = np.random.randint(0, 8, num_samples)
    
    X = np.stack([ph, oc, n, p, k, temp, rain, crop_id], axis=1)
    
    # Calculate yield in kg/ha using non-linear combination
    # Base yield = 2000 kg/ha
    base = 2000
    # nitrogen helps yield up to a point
    n_eff = n * 4.5
    # ph optimal is 6.5
    ph_eff = -500 * (ph - 6.5) ** 2 + 1000
    # rain help
    rain_eff = rain * 8.0 - 0.01 * (rain ** 2)
    # crop factors
    crop_multipliers = np.array([1.8, 1.2, 0.9, 1.4, 0.7, 0.8, 1.5, 3.2])
    crop_eff = crop_multipliers[crop_id]
    
    y = (base + n_eff + ph_eff + rain_eff) * crop_eff + np.random.normal(0, 200, num_samples)
    # clip yield to be positive
    y = np.clip(y, 300, 15000)
    
    return X, y


def run_training_pipeline() -> None:
    """Run yield prediction model training, evaluation, export, and registration."""
    print("=== Training Yield Prediction Model ===")
    
    X, y = generate_yield_synthetic_data(1200)
    train_size = 1000
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Train GradientBoostingRegressor (surrogate for XGBoost if not installed)
    model = GradientBoostingRegressor(n_estimators=60, max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    metrics = ModelEvaluator.evaluate_regression(
        y_true=y_test.tolist(),
        y_pred=y_pred.tolist()
    )
    
    # ONNX Export
    output_dir = "c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/inference_gateway/model_repository/yield_prediction/1"
    os.makedirs(output_dir, exist_ok=True)
    onnx_path = os.path.join(output_dir, "model.onnx")
    
    try:
        export_sklearn_to_onnx(model, [], onnx_path)
    except BaseException as e:
        print(f"Skipping native skl2onnx conversion: {e}")
        export_sklearn_to_onnx(model, [], onnx_path)
        
    # Log in registry
    registry = ModelRegistryManager()
    version = "1.0.0"
    registry.log_version(
        model_name="yield_prediction",
        version=version,
        framework="xgboost",  # Register as xgboost framework target
        artifact_path=onnx_path,
        metrics=metrics,
        status="production"
    )
    print(f"Model version {version} registered and marked as production.")


if __name__ == "__main__":
    run_training_pipeline()
