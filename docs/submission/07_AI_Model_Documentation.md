# AI Model Documentation
## AgriDecision AI — Machine Learning & Inference System Reference
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. AI Architecture Overview

AgriDecision AI implements a **four-model inference portfolio** served via NVIDIA Triton Inference Server with ONNX Runtime:

```
┌─────────────────────────────────────────────────────────────┐
│              Triton Inference Server (Port 8080)             │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Crop Reco   │   Yield Pred │  Disease Det │ Price Forecast │
│  (RF/ONNX)   │  (GBR/ONNX)  │ (ResNet50)   │  (BiLSTM)      │
│  8-class     │  Regression  │  9-class     │  7-day seq     │
└──────────────┴──────────────┴──────────────┴────────────────┘
                         │
            Fallback Rule Engines (when Triton unavailable)
```

---

## 2. Crop Recommendation Model (CRM)

### 2.1 Model Card

| Attribute | Value |
| :--- | :--- |
| **Model Name** | `crop_recommendation_v1` |
| **Algorithm** | Random Forest Classifier |
| **Framework** | Scikit-Learn → ONNX (skl2onnx) |
| **Training Samples** | 1,200 synthetic Indian soil profiles |
| **Feature Dimensionality** | 7 |
| **Output Classes** | 8 |
| **Test Accuracy** | 79.3% |
| **Weighted Precision** | 0.80 |
| **Weighted Recall** | 0.79 |
| **Weighted F1** | 0.79 |
| **ONNX Opset** | 12 |
| **Model File** | `ai_services/training_pipelines/models/crop_recommendation_v1.onnx` |

### 2.2 Input Feature Vector

| Feature | Type | Unit | Agronomic Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ph_level` | float32 | — | 4.5–9.5 | Soil pH |
| `organic_carbon_pct` | float32 | % | 0.1–5.0 | Soil Organic Carbon |
| `nitrogen_content` | float32 | kg/ha | 0–500 | Available Nitrogen |
| `phosphorus_content` | float32 | kg/ha | 0–150 | Available Phosphorus |
| `potassium_content` | float32 | kg/ha | 0–600 | Available Potassium |
| `temperature_c` | float32 | °C | 5–45 | Average temperature |
| `rainfall_mm` | float32 | mm | 200–3000 | Annual precipitation |

**Input Tensor:** `float32[1,7]` — batch_size × feature_count

### 2.3 Output

```
label_index:        int64[1]      — Predicted class index (0–7)
all_probabilities:  float32[1,8] — Softmax probability per class
```

**Class Label Mapping:**
```
0: rice    1: maize    2: soybean    3: wheat
4: chickpea  5: mustard  6: cotton   7: sugarcane
```

### 2.4 Hyperparameters

```python
RandomForestClassifier(
    n_estimators = 50,
    max_depth = None,
    min_samples_split = 2,
    min_samples_leaf = 1,
    class_weight = 'balanced',
    random_state = 42,
    n_jobs = 1          # Thread-safe for concurrent inference
)
```

### 2.5 Training Pipeline

File: `ai_services/training_pipelines/trainers/crop_recommendation.py`

```python
# Simplified training flow
1. Generate synthetic dataset (1200 samples, 7 features, 8 classes)
2. Split: 80% train / 20% test (random_state=42)
3. Train RandomForestClassifier
4. Evaluate: accuracy, classification_report, confusion matrix
5. Register in ModelRegistry (SQLAlchemy SQLite)
6. Export: export_sklearn_to_onnx(model, 7 features) → .onnx file
```

### 2.6 SHAP Explainability

- **Method:** TreeSHAP via `shap.TreeExplainer`
- **Output:** Per-feature SHAP values normalized to sum to 1.0
- **Fallback:** Equal weight attribution (1/7 per feature) when `shap` unavailable
- **Delivery:** Included in every recommendation API response as `shap_values` dict

---

## 3. Yield Prediction Model (YPM)

### 3.1 Model Card

| Attribute | Value |
| :--- | :--- |
| **Model Name** | `yield_prediction_v1` |
| **Algorithm** | Gradient Boosting Regressor |
| **Framework** | Scikit-Learn → ONNX (skl2onnx) |
| **Training Samples** | 1,200 synthetic yield records |
| **Feature Dimensionality** | 8 |
| **Test RMSE** | 459.31 kg/ha |
| **Test MAE** | 311.8 kg/ha |
| **Test R²** | 0.82 |
| **ONNX Opset** | 12 |
| **Model File** | `ai_services/training_pipelines/models/yield_prediction_v1.onnx` |

### 3.2 Input Feature Vector

Same 7 features as CRM + `crop_type_index` (int32 → float32 cast, 0–7 same label mapping).

**Input Tensor:** `float32[1,8]`

### 3.3 Output

```
predicted_yield:   float32[1] — Expected yield in kg/ha
```

### 3.4 Hyperparameters

```python
GradientBoostingRegressor(
    n_estimators = 60,
    max_depth = 4,
    learning_rate = 0.10,
    subsample = 0.8,
    random_state = 42
)
```

---

## 4. Disease Detection CNN (DDM)

### 4.1 Model Card

| Attribute | Value |
| :--- | :--- |
| **Model Name** | `disease_detection_v1` |
| **Architecture** | ResNet-50 (pre-trained ImageNet) |
| **Framework** | PyTorch → ONNX (opset 14) |
| **Training Dataset** | PlantVillage 87,000 images (38 classes → 9 Indian categories) |
| **Input Resolution** | 224×224 RGB |
| **Output Classes** | 9 |
| **Test Precision** | 0.88 |
| **Test Recall** | 0.86 |
| **Test F1** | 0.87 |
| **ONNX Opset** | 14 |
| **Model File** | `ai_services/training_pipelines/models/disease_detection_v1.onnx` |

### 4.2 Class Labels

```
0: healthy          1: leaf_rust          2: powdery_mildew
3: bacterial_blight 4: leaf_spot          5: stem_rot
6: downy_mildew     7: aphid_infestation  8: early_blight
```

### 4.3 Input Preprocessing

```python
transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

**Input Tensor:** `float32[1, 3, 224, 224]` — batch × channels × H × W

### 4.4 Output

```
logits:       float32[1, 9]  — Raw logits before softmax
probabilities: float32[1, 9] — Softmax normalized class probabilities
predicted_class_index: int64[1]
```

### 4.5 Model Architecture

```python
class DiseaseCNN(nn.Module):
    def __init__(self, num_classes=9):
        super().__init__()
        self.backbone = models.resnet50(pretrained=True)
        # Replace final classification head
        in_features = self.backbone.fc.in_features  # 2048
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
```

### 4.6 Grad-CAM Explainability

- **Target Layer:** `backbone.layer4[-1]` (final ResNet residual block)
- **Computation:** Gradient of target class score w.r.t. layer4 feature maps
- **Output:** 224×224 normalized heatmap overlaid (red=high attention) on original image
- **Storage:** Uploaded to S3 at `gradcam/{scan_id}.jpg`
- **Fallback:** Random normalized heatmap mask when PyTorch unavailable (testing only)

### 4.7 Triton Configuration

```
# ai_services/inference_gateway/triton_models/disease_detection_v1/config.pbtxt
platform: "onnxruntime_onnx"
max_batch_size: 8
dynamic_batching {
    preferred_batch_size: [2, 4, 8]
    max_queue_delay_microseconds: 5000
}
instance_group [{ count: 2 kind: KIND_CPU }]
```

---

## 5. Price Forecasting LSTM (PFM)

### 5.1 Model Card

| Attribute | Value |
| :--- | :--- |
| **Model Name** | `price_forecasting_v1` |
| **Architecture** | Bidirectional LSTM + Bahdanau Attention |
| **Framework** | PyTorch → ONNX (torch.export) |
| **Training Dataset** | 5-year Agmarknet daily prices, 7 commodities |
| **Input Window** | 30 days |
| **Output Horizon** | 7 days |
| **Test MAE** | 42.5 INR/quintal |
| **Test RMSE** | 58.3 INR/quintal |

### 5.2 Architecture Details

```python
class PriceForecastLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=128, num_layers=2, output_size=7):
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        # Bahdanau Attention
        self.attention = nn.Linear(hidden_size * 2, 1)
        # Output
        self.fc = nn.Linear(hidden_size * 2, output_size)
```

**Input Tensor:** `float32[1, 30, 1]` — batch × sequence × features  
**Output Tensor:** `float32[1, 7]` — batch × forecast_days

---

## 6. Federated Learning Architecture

### 6.1 Purpose

`ai_services/federated_learning/` provides the scaffolding for privacy-preserving on-device model updates, enabling participating farmer IoT nodes to contribute model improvements without sharing raw farm data.

### 6.2 Components

| File | Role |
| :--- | :--- |
| `fl_orchestrator.py` | Central FL server: aggregates model weight updates from clients |
| `fl_client.py` | Client-side: trains on local data, returns encrypted weight deltas |
| `aggregator.py` | Federated averaging (FedAvg) with differential privacy noise injection |
| `secure_aggregation.py` | Secret-sharing protocol for gradient encryption |

### 6.3 FedAvg Algorithm

```
Global round r:
1. Server broadcasts global model weights W_r to N clients
2. Each client k trains on local data D_k for E epochs → W_k
3. Server aggregates: W_{r+1} = Σ (|D_k| / |D|) * W_k
4. Repeat until convergence or max_rounds
```

---

## 7. Model Registry

### 7.1 Purpose

All model artifacts are versioned and tracked via `ai_services/model_registry/registry.py` — a SQLAlchemy-backed SQLite registry.

### 7.2 Registry Schema

**`model_versions` table:**
```
id          INTEGER PK
name        TEXT          — Model name (crop_recommendation_v1)
version     TEXT          — Semantic version (1.0.0)
framework   TEXT          — sklearn / pytorch / onnx
artifact_path TEXT        — Filesystem path to .onnx file
status      TEXT          — staging / production / archived
created_at  TIMESTAMP
```

**`model_metrics` table:**
```
id              INTEGER PK
model_version_id INTEGER FK
metric_name     TEXT       — accuracy / precision / recall / f1 / rmse / mae
metric_value    REAL
split           TEXT       — train / val / test
logged_at       TIMESTAMP
```

---

## 8. Model Monitoring & Drift Detection

### 8.1 Purpose

`ai_services/monitoring/drift_detector.py` implements `DriftTelemetryDetector` for continuous monitoring of production model input distribution shifts.

### 8.2 Detection Methods

**Kolmogorov-Smirnov (KS) Test:**
```python
from scipy.stats import ks_2samp
statistic, p_value = ks_2samp(reference_distribution, current_distribution)
# Alert threshold: p_value < 0.05 and statistic > 0.10
```

**Population Stability Index (PSI):**
```python
PSI = Σ (actual_pct - expected_pct) * ln(actual_pct / expected_pct)
# Alert threshold: PSI > 0.25 (significant drift)
```

### 8.3 Drift Monitoring Pipeline

1. Collect last 7 days of live inference input features
2. Compare against training-time reference distribution
3. Compute KS statistic + PSI per feature
4. If drift detected: emit Prometheus metric `model_drift_score{model="crop_recommendation_v1", feature="ph_level"}`
5. Alert via Grafana AlertManager → notification_service → Admin SMS/Email
