# Installation Guide
## AgriDecision AI — System Installation & Setup Blueprint
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. System Requirements & Environment Checklist

### 1.1 Hardware Specifications

| Component | Minimum (Development) | Recommended (Production) |
| :--- | :--- | :--- |
| **CPU** | 4 Cores (x86_64) | 16+ Cores (EKS m5.xlarge cluster) |
| **RAM** | 8 GB | 32 GB+ |
| **Disk** | 50 GB SSD | 500 GB+ Provisioned IOPS SSD |
| **GPU** | Not required (CPU ONNX Fallback) | NVIDIA T4 / A10G (Triton Inference) |

---

## 2. Step-by-Step Installation Procedure

### Step 1: Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/agridecision/agridecision-ai.git
cd agridecision-ai

# Create Python 3.11 virtual environment
python -m venv venv
# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
cp .env.example .env
```
Modify `.env` with initial development settings:
```ini
POSTGRES_USER=agri_user
POSTGRES_PASSWORD=agri_secure_pass_2026
POSTGRES_DB=agri_db
TIMESCALE_DB=agri_timeseries
REDIS_HOST=localhost
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
VAULT_ADDR=http://localhost:8200
```

### Step 3: Launch Local Datastores & Infra via Docker Compose

```bash
docker-compose up -d agri-postgres agri-timescaledb agri-redis agri-zookeeper agri-kafka agri-kong agri-vault agri-prometheus agri-grafana agri-loki agri-tempo
```

Check container health:
```bash
docker-compose ps
```

### Step 4: Database Schema Initialization

```bash
# 1. Apply Master PostgreSQL Schema
docker exec -i agri-postgres psql -U agri_user -d agri_db < database/postgresql/001_master_schema.sql

# 2. Apply TimescaleDB Hypertables & Continuous Aggregates
docker exec -i agri-timescaledb psql -U agri_user -d agri_timeseries < database/timescaledb/002_timescaledb_hypertables.sql

# 3. Apply JanusGraph Property Graph Schema (Requires Gremlin Console)
# bin/gremlin.sh < database/janusgraph/003_janusgraph_schema.groovy
```

### Step 5: Vault Initialization & Secret Seeding

```bash
# Execute Vault bootstrap script
bash devops/vault/vault-init.sh
```

### Step 6: Train & Export AI Models

```bash
# Train Crop Recommendation Random Forest Model & export ONNX
python ai_services/training_pipelines/trainers/crop_recommendation.py

# Train Yield Prediction Gradient Boosting Regressor & export ONNX
python ai_services/training_pipelines/trainers/yield_prediction.py

# Train Disease Detection CNN (Uses ResNet-50 backbone)
python ai_services/training_pipelines/trainers/disease_detection.py

# Train Commodity Price Forecasting BiLSTM
python ai_services/training_pipelines/trainers/price_forecasting.py
```

### Step 7: Launch Microservices

Run services using Uvicorn or start background tasks:

```bash
# Service ports: 8001 to 8009
uvicorn backend.services.user_service.src.main:app --port 8001 &
uvicorn backend.services.farm_service.src.main:app --port 8002 &
uvicorn backend.services.advisory_service.src.main:app --port 8003 &
uvicorn backend.services.iot_service.src.main:app --port 8004 &
uvicorn backend.services.market_service.src.main:app --port 8005 &
uvicorn backend.services.weather_service.src.main:app --port 8006 &
uvicorn backend.services.financial_service.src.main:app --port 8007 &
uvicorn backend.services.enterprise_service.src.main:app --port 8008 &
uvicorn backend.services.notification_service.src.main:app --port 8009 &
```

### Step 8: Build & Launch Web Frontend

```bash
cd frontend/apps/agronomist-portal
npm install
npm run build
npm run dev
```

### Step 9: Launch Mobile Application

```bash
cd mobile
flutter pub get
flutter run
```

---

## 3. Verification & Health Verification

Run the end-to-end AI system verification script:
```bash
python testing/run_ai_system_verification.py
```
Expected Output:
```
======================================================================
  AGRIDECISION AI — SYSTEM VERIFICATION COMPLETE
  RESULT: 6 / 6 STEPS PASSED (100% SUCCESS RATE)
======================================================================
```
