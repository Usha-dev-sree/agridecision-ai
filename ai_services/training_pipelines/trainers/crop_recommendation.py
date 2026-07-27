"""
Training Pipeline - Crop Recommendation Model
Generates synthetic agricultural data matching Indian soil profiles,
trains a Scikit-Learn RandomForest classifier, evaluates metrics,
exports the model to ONNX, and registers it.
"""
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ai_services.model_registry.registry import ModelRegistryManager
from ai_services.training_pipelines.evaluators.metrics import ModelEvaluator
from ai_services.training_pipelines.exporters.onnx_exporter import export_sklearn_to_onnx

# Crop mapping
CROPS = ["rice", "maize", "soybean", "wheat", "chickpea", "mustard", "cotton", "sugarcane"]


def generate_synthetic_data(num_samples: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic soil and weather training data based on rules."""
    np.random.seed(42)
    # Features:
    # 0: ph_level [4.5, 9.5]
    # 1: organic_carbon_percent [0.1, 2.5]
    # 2: nitrogen_content [50, 400]
    # 3: phosphorus_content [5, 120]
    # 4: potassium_content [50, 500]
    # 5: avg_temp_c [15, 38]
    # 6: precipitation_mm [20, 300]
    
    ph = np.random.uniform(4.5, 9.5, num_samples)
    oc = np.random.uniform(0.1, 2.5, num_samples)
    n = np.random.uniform(50, 400, num_samples)
    p = np.random.uniform(5, 120, num_samples)
    k = np.random.uniform(50, 500, num_samples)
    temp = np.random.uniform(15, 38, num_samples)
    rain = np.random.uniform(20, 300, num_samples)
    
    X = np.stack([ph, oc, n, p, k, temp, rain], axis=1)
    y = np.zeros(num_samples, dtype=int)
    
    # Assign crops logically based on conditions
    for i in range(num_samples):
        # Rice likes high rain & high nitrogen
        if rain[i] > 180 and n[i] > 150:
            y[i] = 0  # rice
        # Wheat likes cool temp, moderate rain, Rabi season
        elif temp[i] < 22 and rain[i] < 100 and ph[i] > 6.0:
            y[i] = 3  # wheat
        # Chickpea & mustard like low rain & medium pH
        elif rain[i] < 60 and 6.0 <= ph[i] <= 7.5:
            y[i] = 4 if np.random.rand() > 0.5 else 5  # chickpea or mustard
        # Cotton likes hot temp, medium rain
        elif temp[i] > 28 and 80 < rain[i] < 160:
            y[i] = 6  # cotton
        # Sugarcane likes high rain, hot temp
        elif rain[i] > 150 and temp[i] > 26:
            y[i] = 7  # sugarcane
        # Maize and soybean as default
        else:
            y[i] = 1 if np.random.rand() > 0.5 else 2  # maize or soybean
            
    return X, y


def run_training_pipeline() -> None:
    """Run full model training, evaluation, export, and registration."""
    print("=== Training Crop Recommendation Model ===")
    
    # 1. Generate & Split Data
    X, y = generate_synthetic_data(1200)
    train_size = 1000
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # 2. Train Model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # 3. Evaluate Model
    y_pred = model.predict(X_test)
    metrics = ModelEvaluator.evaluate_classification(
        y_true=y_test.tolist(),
        y_pred=y_pred.tolist()
    )
    
    # 4. Save & Export to ONNX
    output_dir = "c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/inference_gateway/model_repository/crop_recommendation/1"
    os.makedirs(output_dir, exist_ok=True)
    onnx_path = os.path.join(output_dir, "model.onnx")
    
    try:
        from skl2onnx.common.data_types import FloatTensorType
        initial_types = [("float_input", FloatTensorType([None, 7]))]
        export_sklearn_to_onnx(model, initial_types, onnx_path)
    except Exception as e:
        print(f"Skipping native skl2onnx conversion: {e}")
        # Call mock exporter
        export_sklearn_to_onnx(model, [], onnx_path)
        
    # 5. Log in Model Registry
    registry = ModelRegistryManager()
    version = "1.0.0"
    registry.log_version(
        model_name="crop_recommendation",
        version=version,
        framework="scikit-learn",
        artifact_path=onnx_path,
        metrics=metrics,
        status="production"
    )
    print(f"Model version {version} registered and marked as production.")


if __name__ == "__main__":
    run_training_pipeline()
