# Software Design Document (SDD)
## AgriDecision AI — Intelligent Precision Agriculture Platform
**Document Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Introduction

### 1.1 Purpose
This SDD describes the detailed software design for AgriDecision AI, mapping every functional requirement to its implementing component, module, class, and interface.

### 1.2 Design Principles

- **Domain-Driven Design (DDD):** Each microservice owns a bounded context with its own schema and data store.
- **Hexagonal Architecture:** Domain logic decoupled from I/O via repository and service layers.
- **Event-Driven:** Side effects (notifications, feature store updates, audit logs) routed through Kafka topics.
- **Defense in Depth:** Security applied at gateway, service, database, and infrastructure layers independently.
- **Observable by Default:** Every service ships with structured logging, Prometheus metrics, and OpenTelemetry spans.

---

## 2. System Architecture Design

### 2.1 Deployment Architecture

```
Internet
    │
    ▼
┌──────────────┐
│ Kong Gateway  │  JWT Validation, Rate Limit, CORS, TLS Termination
│  Port 8000   │
└──────┬───────┘
       │ Routes by path prefix
       ▼
┌────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                  │
│  Namespace: agridecision-prod                        │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ user-service  │  │ farm-service  │  │ advisory  │ │
│  │  :8001        │  │  :8002        │  │ service   │ │
│  └──────────────┘  └──────────────┘  │  :8003    │ │
│                                        └───────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ iot-service   │  │ market-svc   │  │ weather   │ │
│  │  :8004        │  │  :8005        │  │ service   │ │
│  └──────────────┘  └──────────────┘  │  :8006    │ │
│                                        └───────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ financial-svc │  │ enterprise   │  │ notif-svc │ │
│  │  :8007        │  │ service:8008  │  │  :8009   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │           Data Infrastructure                  │ │
│  │  PostgreSQL  TimescaleDB  Redis   Kafka         │ │
│  │  :5432       :5433         :6379  :9092         │ │
│  └────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

### 2.2 Module Dependency Graph

```
user_service
  └── PostgreSQL (iam schema)
  └── Redis (session tokens)
  └── Vault (JWT signing keys)

farm_service
  └── PostgreSQL (farm schema) + PostGIS
  └── TimescaleDB (sensor/weather hypertables)
  └── user_service [internal HTTP for user validation]

advisory_service
  └── farm_service [internal HTTP for soil profile]
  └── Triton Inference Server [HTTP]
  └── JanusGraph [Gremlin websocket]
  └── Kafka Producer (advisory.results topic)

iot_service
  └── TimescaleDB (timeseries schema)
  └── Kafka Consumer (iot.telemetry.raw topic)
  └── farm_service [internal HTTP for plot validation]

notification_service
  └── Kafka Consumer (notification.events topic)
  └── Twilio (SMS)
  └── Firebase Cloud Messaging (FCM Push)
  └── SendGrid (Email)
```

---

## 3. Detailed Module Design

### 3.1 user_service Module Design

```
user_service/
├── src/
│   ├── main.py              FastAPI application factory, lifespan events
│   ├── config.py            Pydantic Settings (env vars, Vault URLs, JWT keys)
│   ├── dependencies.py      Dependency injection (get_db, get_redis, get_current_user)
│   ├── models/
│   │   ├── user.py          SQLAlchemy User model (iam.user table)
│   │   ├── session.py       UserSession model (iam.user_session table)
│   │   ├── subscription.py  Subscription model (iam.subscription table)
│   │   └── audit_log.py     AuditLog model (iam.audit_log table)
│   ├── repositories/
│   │   ├── user_repository.py      CRUD operations on iam.user
│   │   ├── session_repository.py   JWT session management with Redis
│   │   └── subscription_repository.py  Subscription management
│   ├── services/
│   │   ├── auth_service.py    OTP flow, JWT issuance, token refresh
│   │   ├── mfa_service.py     TOTP generation, QR code, verification
│   │   ├── oauth_service.py   Google/Apple ID token verification
│   │   └── gdpr_service.py    Data export, anonymization, deletion
│   ├── routers/
│   │   ├── auth.py           /v1/auth/* endpoints
│   │   └── users.py          /v1/users/* endpoints
│   └── schemas/
│       ├── auth.py           OTPRequest, OTPVerify, TokenResponse, MFA* schemas
│       └── user.py           UserCreate, UserResponse, UserUpdate schemas
```

**Key Design Decisions:**
- Repository pattern isolates SQLAlchemy queries from service logic
- AuthService encapsulates OTP lifecycle: `request_otp()` → stores in Redis; `verify_otp()` → validates, issues JWT pair
- JWT access tokens: RS256 signed, 15-minute TTL, include `user_id`, `role`, `jti`
- JWT refresh tokens: stored in Redis with `jti` key, 7-day TTL, blacklisted on logout

### 3.2 farm_service Module Design

```
farm_service/
├── src/
│   ├── models/
│   │   ├── farm_plot.py        FarmPlot model (farm.farm_plot)
│   │   ├── plot_boundary.py    PlotBoundary model (farm.plot_boundary, GeoJSON JSONB)
│   │   ├── soil.py             SoilProfile model (farm.soil_profile)
│   │   └── crop_season.py      CropSeason model (farm.crop_season)
│   ├── repositories/
│   │   ├── plot_repository.py   Farm CRUD, PostGIS spatial queries
│   │   └── soil_repository.py   Soil profile CRUD
│   ├── services/
│   │   ├── parcel_service.py    Business logic for farm plot management
│   │   └── satellite_service.py NDVI ingestion from Sentinel-2
│   ├── events/
│   │   └── consumer.py          Kafka consumer for IoT telemetry correlation
│   ├── routers/
│   │   ├── boundaries.py        /v1/farms/{id}/boundary endpoints
│   │   └── farms.py             /v1/farms/* endpoints
│   └── schemas/
│       └── soil.py              SoilProfileCreate, SoilProfileResponse, ValidationReport
```

**PostGIS Spatial Design:**
- Boundary stored as GeoJSON JSONB (native PostgreSQL) with PostGIS `ST_GeomFromGeoJSON()` for spatial indexing
- GIST index on `geom` column enables fast `ST_DWithin()` proximity queries
- Centroid computed via `ST_Centroid(ST_GeomFromGeoJSON(geojson))` and stored as NUMERIC lat/lng

### 3.3 advisory_service Module Design

```
advisory_service/
├── src/
│   ├── services/
│   │   └── diagnosis_service.py   Orchestrates: soil fetch → feature vector → Triton → SHAP → DB log
│   ├── routers/
│   │   └── diagnosis.py           /v1/diagnosis/* endpoints
│   └── events/
│       └── consumer.py            Kafka consumer for async advisory processing
```

**AI Inference Flow Design:**

```
1. POST /v1/diagnosis/crop-recommendation (soil_profile_id)
   │
   ├── fetch SoilProfile from farm_service
   ├── build feature_vector = [ph, oc, n, p, k, temp, rain]
   ├── POST Triton /v2/models/crop_recommendation/infer
   │   └── Returns: {label_index, class_probabilities[]}
   ├── build SHAP = ShapTabularExplainer.explain(predict_fn, feature_vector)
   ├── INSERT advisory.recommendation (model_version, recommended_crop, confidence, shap_values)
   ├── Kafka.produce("advisory.results", {user_id, plot_id, recommendation})
   └── Return: {recommended_crop, confidence, shap_values, reasoning}
```

### 3.4 AI Services Module Design

```
ai_services/
├── feature_store/
│   ├── materialization/
│   │   └── engine.py        FeatureStoreEngine: Redis-backed feature materialization
│   └── validation/
│       └── expectations.py  FeatureValidator: soil bounds, weather bounds, price bounds
│
├── inference_gateway/
│   ├── triton_client.py     TritonInferenceClient: async HTTP V2 inference, ONNX fallback
│   ├── explainers.py        ShapTabularExplainer, GradCamExplainer
│   └── fallback_rules.py    Rule-based fallback engines (crop, yield, disease, price)
│
├── model_registry/
│   └── registry.py          ModelRegistryManager: SQLAlchemy + SQLite registry
│
├── monitoring/
│   └── drift_detector.py    DriftTelemetryDetector: KS test, PSI computation
│
├── training_pipelines/
│   ├── trainers/
│   │   ├── crop_recommendation.py   RF classifier training pipeline
│   │   ├── yield_prediction.py      GBR training pipeline
│   │   ├── price_forecasting.py     BiLSTM training pipeline (PyTorch fallback)
│   │   └── disease_detection.py     ResNet-50 CNN training (PyTorch fallback)
│   ├── evaluators/
│   │   └── metrics.py               ModelEvaluator: classification + regression metrics
│   └── exporters/
│       └── onnx_exporter.py         export_sklearn_to_onnx, export_pytorch_to_onnx
│
└── voice_vis_engine/
    └── src/
        ├── voice_processor.py   VoiceProcessor: ASR (Whisper/gTTS stub), TTS
        └── prompt_engine.py     AgronomicPromptEngine: local rule-based + LLM advisory
```

---

## 4. Database Design

### 4.1 Entity-Relationship Summary

**Core Entities:**
- `iam.user` (1) ←→ (many) `farm.farm_plot`
- `farm.farm_plot` (1) ←→ (1) `farm.plot_boundary`
- `farm.farm_plot` (1) ←→ (1) `farm.soil_profile`
- `farm.farm_plot` (1) ←→ (many) `farm.crop_season`
- `farm.farm_plot` (1) ←→ (many) `farm.iot_device`
- `iam.user` (1) ←→ (many) `advisory.recommendation`
- `iam.user` (1) ←→ (many) `advisory.disease_scan`
- `iam.user` (1) ←→ (many) `financial.loan_application`
- `farm.farm_plot` (many) ←→ (many) `financial.contract` (via `enterprise.contract_plots`)

### 4.2 Key SQLAlchemy Model Attributes

**FarmPlot:**
```python
id: UUID (PK)
owner_id: UUID (FK → iam.user.id, CASCADE DELETE)
name: str (max 100)
total_area_ha: Decimal (10,4)
irrigation_type: str  # RAINFED | CANAL | DRIP | SPRINKLER
is_active: bool
centroid_lat: Optional[Decimal] (9,6)
centroid_lng: Optional[Decimal] (9,6)
created_at: datetime (TZ-aware)
updated_at: datetime (TZ-aware, auto-update)
```

**SoilProfile:**
```python
id: UUID (PK)
plot_id: UUID (FK → farm.farm_plot.id, CASCADE DELETE)
ph_level: Decimal (4,2)           # bounds: 4.5–9.5
organic_carbon_pct: Decimal (5,3) # bounds: 0.1–5.0
nitrogen_content: Decimal (7,2)   # kg/ha, bounds: 0–500
phosphorus_content: Decimal (7,2) # kg/ha, bounds: 0–150
potassium_content: Decimal (7,2)  # kg/ha, bounds: 0–600
electrical_conductivity: Decimal (6,3) # dS/m
sampled_at: datetime
```

### 4.3 TimescaleDB Hypertable Schema

**`timeseries.weather_observations`:**
```sql
time                TIMESTAMPTZ     -- Partition key, 7-day chunks
farm_plot_id        UUID            -- Hash dimension, 4 partitions
source              VARCHAR(30)     -- OPENWEATHER | IMD | IOT_STATION
temp_c              NUMERIC(6,3)
rainfall_mm         NUMERIC(8,3)
evapotranspiration_mm NUMERIC(8,4) -- FAO-56 computed ET₀
solar_radiation_mj  NUMERIC(8,4)
uv_index            NUMERIC(5,2)
raw_api_response    JSONB
```

**Continuous Aggregate:** `weather_daily_summary` (materialized view)  
```sql
SELECT time_bucket('1 day', time) AS day,
       farm_plot_id,
       AVG(temp_c), SUM(rainfall_mm), AVG(evapotranspiration_mm)
FROM timeseries.weather_observations
GROUP BY day, farm_plot_id;
```

---

## 5. API Design Patterns

### 5.1 URL Convention
- All endpoints versioned under `/v1/`
- Resource naming: plural nouns (e.g., `/v1/farms/`, `/v1/users/`)
- Sub-resources via path: `/v1/farms/{farm_id}/soil`
- Actions as POST to sub-resource: `/v1/auth/request-otp`

### 5.2 Authentication Header Pattern
```
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

### 5.3 Standard Response Envelope
Success (200/201):
```json
{
  "data": { ... },
  "metadata": { "version": "1.0", "request_id": "<uuid>", "timestamp": "<iso8601>" }
}
```

Error (4xx/5xx):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [...]
  }
}
```

### 5.4 Pagination Pattern
```
GET /v1/farms/?page=1&per_page=20
Response: { "data": [...], "total": 150, "page": 1, "per_page": 20, "pages": 8 }
```

---

## 6. Security Design

### 6.1 JWT Architecture

```
Access Token (15 min TTL):
{
  "sub": "<user_uuid>",
  "role": "FARMER",
  "jti": "<uuid>",    ← Used for blacklisting on logout
  "iat": 1722178034,
  "exp": 1722178934
}
Algorithm: RS256
Signed with: RSA private key from Vault kv/data/agri/jwt
Verified with: RSA public key (Kong JWT plugin)
```

### 6.2 Vault Secret Paths

```
kv/data/agri/database     → DB_URL, TIMESCALE_URL
kv/data/agri/redis        → REDIS_URL, REDIS_PASSWORD
kv/data/agri/kafka        → KAFKA_BOOTSTRAP_SERVERS
kv/data/agri/jwt          → JWT_PRIVATE_KEY, JWT_PUBLIC_KEY
kv/data/agri/external     → OPENWEATHER_API_KEY, GOOGLE_CLIENT_ID, TWILIO_AUTH_TOKEN
```

### 6.3 Kong Plugin Pipeline

Request lifecycle through Kong:
```
Request → [CORS Plugin] → [JWT Plugin] → [Rate Limiting Plugin] → Backend Service
Response ← [Response Transformer (OWASP headers)] ← Backend Service
```

---

## 7. Error Handling Strategy

- All service layer exceptions caught and wrapped in `AgriDecisionException` hierarchy
- HTTP 422: Pydantic validation failures (body/query params)
- HTTP 401: Expired or invalid JWT
- HTTP 403: Insufficient RBAC role
- HTTP 404: Resource not found
- HTTP 429: Rate limit exceeded (Kong)
- HTTP 500: Unhandled service exception (logged to Loki, traced to Tempo)
- AI inference failures: Fallback rule engine invoked automatically, response flagged with `"fallback_used": true`
