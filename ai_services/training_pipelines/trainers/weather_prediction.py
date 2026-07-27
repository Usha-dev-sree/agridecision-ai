"""
Training Pipeline - Weather Prediction Model
Trains a Scikit-Learn / GradientBoostingRegressor model for micro-climate weather forecasting
(temperature, precipitation, and humidity) for farm plots.
Evaluates performance metrics, exports to ONNX, and registers in the Model Registry.
"""
import os
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from ai_services.model_registry.registry import ModelRegistryManager
from ai_services.training_pipelines.evaluators.metrics import ModelEvaluator
from ai_services.training_pipelines.exporters.onnx_exporter import export_sklearn_to_onnx


def generate_synthetic_weather_data(num_samples: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic weather sequence data.
    Features (5 inputs):
      0: latitude [-90 to 90]
      1: longitude [-180 to 180]
      2: day_of_year [1 to 365]
      3: current_temp_c [10 to 45]
      4: current_humidity_pct [20 to 95]
    Targets (3 outputs):
      [expected_temp_max_c, expected_rainfall_mm, expected_humidity_pct]
    """
    np.random.seed(42)
    lat = np.random.uniform(8.0, 37.0, num_samples)  # India latitude range
    lon = np.random.uniform(68.0, 97.0, num_samples) # India longitude range
    doy = np.random.uniform(1, 365, num_samples)
    curr_temp = np.random.uniform(15, 42, num_samples)
    curr_hum = np.random.uniform(30, 90, num_samples)

    X = np.stack([lat, lon, doy, curr_temp, curr_hum], axis=1)

    # Calculate realistic next-day target values using seasonal sinusoidal signals
    temp_max = curr_temp + np.sin(2 * np.pi * doy / 365.0) * 3.0 + np.random.normal(0, 1.5, num_samples)
    rainfall = np.maximum(0.0, np.sin(2 * np.pi * (doy - 150) / 365.0) * 25.0 + (curr_hum / 100.0) * 15.0 + np.random.normal(0, 5.0, num_samples))
    humidity = np.clip(curr_hum + np.random.normal(0, 4.0, num_samples), 20.0, 98.0)

    y = np.stack([temp_max, rainfall, humidity], axis=1)
    return X, y


def run_training_pipeline() -> None:
    """Run weather prediction model training, evaluation, export, and registration."""
    print("=== Training Weather Prediction Model ===")

    X, y = generate_synthetic_weather_data(1200)
    train_size = 1000
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Train multi-output GradientBoosting Regressor or MultiOutputRegressor
    from sklearn.multioutput import MultiOutputRegressor
    base_regressor = GradientBoostingRegressor(n_estimators=50, max_depth=4, random_state=42)
    model = MultiOutputRegressor(base_regressor)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    metrics = ModelEvaluator.evaluate_regression(
        y_true=y_test[:, 0].tolist(), # Evaluate on max temperature prediction
        y_pred=y_pred[:, 0].tolist()
    )

    # ONNX Export
    output_dir = "c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/inference_gateway/model_repository/weather_prediction/1"
    os.makedirs(output_dir, exist_ok=True)
    onnx_path = os.path.join(output_dir, "model.onnx")

    try:
        from skl2onnx.common.data_types import FloatTensorType
        initial_types = [("float_input", FloatTensorType([None, 5]))]
        export_sklearn_to_onnx(model, initial_types, onnx_path)
    except Exception as e:
        print(f"Skipping native skl2onnx conversion: {e}")
        export_sklearn_to_onnx(model, [], onnx_path)

    # Log in model registry
    registry = ModelRegistryManager()
    version = "1.0.0"
    registry.log_version(
        model_name="weather_prediction",
        version=version,
        framework="scikit-learn",
        artifact_path=onnx_path,
        metrics=metrics,
        status="production"
    )
    print(f"Weather prediction model version {version} registered and marked as production.")


if __name__ == "__main__":
    run_training_pipeline()
