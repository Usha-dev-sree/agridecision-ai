# Database Documentation
## AgriDecision AI — Polyglot Data Architecture Reference
**Version:** 1.0 | **Date:** July 28, 2026

---

## Overview

AgriDecision AI uses a polyglot persistence architecture with four specialized data stores:

| Store | Type | Use Case | Version |
| :--- | :--- | :--- | :--- |
| PostgreSQL + PostGIS | Relational + Geospatial | Core business data, user/farm/advisory records | 15.x + 3.4 |
| TimescaleDB | Time-Series (PostgreSQL extension) | IoT telemetry, weather observations, market prices | 2.15 |
| Redis | In-Memory Key-Value | Session tokens, OTP cache, feature store, message queue | 7.x |
| JanusGraph | Property Graph | Agri-ontological knowledge base, GraphRAG reasoning | 1.0 |

---

## 1. PostgreSQL + PostGIS Database

### 1.1 Schema Organization

The master PostgreSQL database is divided into isolated schemas:

```
agri_db/
├── iam/         — Identity and Access Management
├── farm/        — Farm, Soil, IoT Device Management
├── advisory/    — AI Recommendations and Diagnostics
├── market/      — Commodity Pricing
├── financial/   — Credit Scoring and Loan Management
└── enterprise/  — Procurement and Contract Management
```

### 1.2 iam Schema

#### Table: `iam.user`

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| id | UUID | PK, NOT NULL | User unique identifier |
| phone_number | VARCHAR(20) | UNIQUE, NOT NULL | Verified mobile number |
| email | VARCHAR(255) | UNIQUE | Optional email address |
| full_name | VARCHAR(150) | NOT NULL | User's full name |
| role | VARCHAR(30) | NOT NULL, CHECK | FARMER / AGRONOMIST / ENTERPRISE / ADMIN / SUPER_ADMIN |
| state | VARCHAR(50) | | Indian state |
| district | VARCHAR(100) | | District of residence |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| mfa_secret | VARCHAR(32) | ENCRYPTED | TOTP secret (pgcrypto AES-256) |
| mfa_enabled | BOOLEAN | DEFAULT FALSE | MFA activation status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_user_phone` — UNIQUE on phone_number
- `idx_user_email` — UNIQUE on email (partial: WHERE email IS NOT NULL)
- `idx_user_role` — on role (for RBAC queries)

#### Table: `iam.user_session`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Session identifier |
| user_id | UUID FK (iam.user, CASCADE) | Session owner |
| device_fingerprint | VARCHAR(255) | Client device identifier |
| jwt_jti | UUID UNIQUE | JWT ID for blacklisting |
| ip_address | INET | Client IP at login |
| user_agent | TEXT | Browser/App user agent |
| expires_at | TIMESTAMPTZ | Session expiry |
| revoked_at | TIMESTAMPTZ | If explicitly revoked |
| created_at | TIMESTAMPTZ | Login timestamp |

#### Table: `iam.audit_log`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Event identifier |
| user_id | UUID FK (nullable) | Performing user |
| action | VARCHAR(100) | Action code (LOGIN, LOGOUT, OTP_REQUEST, etc.) |
| resource | VARCHAR(200) | Affected resource path |
| resource_id | UUID | Affected resource ID |
| outcome | VARCHAR(20) | SUCCESS / FAILURE |
| ip_address | INET | Client IP |
| metadata | JSONB | Additional context |
| timestamp | TIMESTAMPTZ | Event time |

#### Table: `iam.subscription`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Subscription identifier |
| user_id | UUID FK (iam.user, CASCADE) | Subscriber |
| plan_type | VARCHAR(30) | FREE / PRO / ENTERPRISE |
| valid_until | TIMESTAMPTZ | Expiry date |
| features | JSONB | Enabled feature flags |
| created_at | TIMESTAMPTZ | Subscription start |

---

### 1.3 farm Schema

#### Table: `farm.farm_plot`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Plot identifier |
| owner_id | UUID FK (iam.user, CASCADE) | Plot owner |
| name | VARCHAR(100) NOT NULL | Plot display name |
| total_area_ha | NUMERIC(10,4) NOT NULL | Total area in hectares |
| irrigation_type | TEXT NOT NULL | RAINFED / CANAL / DRIP / SPRINKLER |
| is_active | BOOLEAN DEFAULT TRUE | Active status |
| centroid_lat | NUMERIC(9,6) | Latitude of plot centroid |
| centroid_lng | NUMERIC(9,6) | Longitude of plot centroid |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last modified timestamp |

#### Table: `farm.plot_boundary`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Boundary record ID |
| plot_id | UUID FK (farm.farm_plot, CASCADE) | Associated plot |
| geojson | JSONB NOT NULL | GeoJSON Polygon feature |
| geom | GEOMETRY(Polygon, 4326) | PostGIS geometry (from geojson) |
| area_ha | NUMERIC(10,4) | Computed area in hectares |
| perimeter_m | NUMERIC(12,2) | Computed perimeter in meters |
| created_at | TIMESTAMPTZ | Creation timestamp |

**PostGIS Index:** `CREATE INDEX idx_plot_boundary_geom ON farm.plot_boundary USING GIST (geom)`

#### Table: `farm.soil_profile`

| Column | Type | Validation | Description |
| :--- | :--- | :--- | :--- |
| id | UUID PK | | Profile ID |
| plot_id | UUID FK (CASCADE) | | Associated plot |
| ph_level | NUMERIC(4,2) | 4.5–9.5 | Soil pH |
| organic_carbon_pct | NUMERIC(5,3) | 0.1–5.0 | Organic carbon % |
| nitrogen_content | NUMERIC(7,2) | 0–500 | Available Nitrogen kg/ha |
| phosphorus_content | NUMERIC(7,2) | 0–150 | Available Phosphorus kg/ha |
| potassium_content | NUMERIC(7,2) | 0–600 | Available Potassium kg/ha |
| electrical_conductivity | NUMERIC(6,3) | 0–10 | EC in dS/m |
| texture_class | VARCHAR(30) | | SANDY / LOAM / CLAY / SILT / SANDY_LOAM |
| micronutrients | JSONB | | Zn, Fe, Mn, Cu levels |
| sampled_at | TIMESTAMPTZ | | Sample collection date |
| lab_report_url | VARCHAR(500) | | S3 URL to soil test report PDF |

#### Table: `farm.iot_device`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Device ID |
| plot_id | UUID FK (farm.farm_plot) | Associated plot |
| device_type | VARCHAR(30) | SOIL_SENSOR / WEATHER_STATION / WATER_FLOW_METER |
| serial_number | VARCHAR(100) UNIQUE | Hardware serial number |
| firmware_version | VARCHAR(20) | Current firmware version |
| battery_level_pct | SMALLINT | Last reported battery % |
| last_seen | TIMESTAMPTZ | Last telemetry timestamp |
| is_active | BOOLEAN | Device active status |

---

### 1.4 advisory Schema

#### Table: `advisory.recommendation`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Recommendation ID |
| user_id | UUID FK (iam.user) | Requesting user |
| plot_id | UUID FK (farm.farm_plot) | Associated plot |
| model_name | VARCHAR(100) | crop_recommendation_v1 |
| model_version | VARCHAR(20) | e.g., 1.0.0 |
| recommended_crop | VARCHAR(50) | Predicted crop class |
| confidence_score | NUMERIC(5,4) | Model confidence 0–1 |
| all_class_probabilities | JSONB | Full probability distribution |
| shap_values | JSONB | SHAP attribution per feature |
| fallback_used | BOOLEAN | Whether rule-based fallback was applied |
| agronomist_review | TEXT | Optional Agronomist annotation |
| created_at | TIMESTAMPTZ | Recommendation timestamp |

#### Table: `advisory.disease_scan`

| Column | Type | Description |
| :--- | :--- | :--- |
| id | UUID PK | Scan ID |
| user_id | UUID FK (iam.user) | Requesting user |
| image_s3_key | VARCHAR(500) | S3 object key for original image |
| crop_type | VARCHAR(50) | Declared crop type |
| diagnosis_label | VARCHAR(100) | Predicted disease class |
| confidence | NUMERIC(5,4) | Model confidence |
| gradcam_s3_key | VARCHAR(500) | S3 key for Grad-CAM overlay image |
| remedy_prescribed | TEXT[] | List of remedy steps |
| created_at | TIMESTAMPTZ | Scan timestamp |

---

## 2. TimescaleDB Hypertables

### 2.1 Hypertable Summary

All hypertables are created with:
- **Time dimension:** `chunk_time_interval => INTERVAL '7 days'` (weather, NDVI, sensors) or `INTERVAL '1 day'` (prices)
- **Space dimension:** `by_hash('farm_plot_id', 4)` — 4 hash partitions for parallel query execution
- **Retention policy:** 5 years (weather, NDVI), 2 years (sensors), 10 years (prices)
- **Compression policy:** Compress chunks older than 30 days

### 2.2 `timeseries.weather_observations`

Primary time-series store for agrometeorological data from all sources.

| Column | Type | Source |
| :--- | :--- | :--- |
| time | TIMESTAMPTZ | Partition key |
| farm_plot_id | UUID | Hash dimension |
| source | VARCHAR(30) | OPENWEATHER / IMD / IOT_STATION / MANUAL |
| temp_c | NUMERIC(6,3) | Air temperature |
| temp_min_c | NUMERIC(6,3) | Daily minimum |
| temp_max_c | NUMERIC(6,3) | Daily maximum |
| humidity_pct | NUMERIC(5,2) | Relative humidity |
| wind_speed_ms | NUMERIC(7,3) | Wind speed |
| rainfall_mm | NUMERIC(8,3) | Precipitation |
| solar_radiation_mj | NUMERIC(8,4) | MJ/m² |
| evapotranspiration_mm | NUMERIC(8,4) | FAO-56 ET₀ |
| uv_index | NUMERIC(5,2) | UV Index |
| raw_api_response | JSONB | Full API payload |

**Continuous Aggregate:** `weather_daily_summary` (materialized, refreshed every 1 hour)

### 2.3 `timeseries.ndvi_observations`

Satellite vegetation index tracking (Sentinel-2 based).

| Column | Type | Description |
| :--- | :--- | :--- |
| time | TIMESTAMPTZ | Observation timestamp |
| farm_plot_id | UUID | Associated plot |
| ndvi_score | NUMERIC(5,4) | NDVI (-1 to 1) |
| evi_score | NUMERIC(5,4) | Enhanced Vegetation Index |
| cloud_cover_pct | NUMERIC(5,2) | Cloud coverage at capture time |
| satellite_pass | VARCHAR(20) | Sentinel-2A / Sentinel-2B |
| image_s3_key | VARCHAR(500) | S3 URL to false-color composite |

### 2.4 `timeseries.sensor_readings`

Raw IoT sensor telemetry from registered field devices.

| Column | Type | Description |
| :--- | :--- | :--- |
| time | TIMESTAMPTZ | Reading timestamp |
| device_id | UUID | Registered device |
| farm_plot_id | UUID | Associated plot |
| soil_temp_c | NUMERIC(6,3) | Soil temperature |
| soil_moisture_pct | NUMERIC(5,2) | Volumetric soil moisture |
| conductivity_ds_m | NUMERIC(6,3) | Electrical conductivity |
| air_temp_c | NUMERIC(6,3) | Air temperature |
| air_humidity_pct | NUMERIC(5,2) | Relative humidity |
| battery_voltage | NUMERIC(4,2) | Battery voltage |
| signal_strength_dbm | SMALLINT | RSSI |
| raw_payload | JSONB | Raw MQTT payload |

### 2.5 `timeseries.market_prices`

Mandi commodity price time series (from Agmarknet integration).

| Column | Type | Description |
| :--- | :--- | :--- |
| time | TIMESTAMPTZ | Price date |
| commodity_code | VARCHAR(30) | WHEAT / RICE / SOYBEAN etc. |
| mandi_code | VARCHAR(50) | Mandi identifier |
| state | VARCHAR(50) | State |
| min_price_inr | NUMERIC(10,2) | Minimum price |
| max_price_inr | NUMERIC(10,2) | Maximum price |
| modal_price_inr | NUMERIC(10,2) | Modal (most frequent) price |
| volume_mt | NUMERIC(12,3) | Arrivals volume (metric tons) |

---

## 3. Redis Key-Value Store

### 3.1 Key Schema

| Pattern | TTL | Usage |
| :--- | :--- | :--- |
| `otp:{phone_number}` | 600s (10 min) | OTP storage for verification |
| `jwt:blacklist:{jti}` | 604800s (7 days) | Revoked JWT token JTIs |
| `session:{user_id}` | 900s (15 min) | Active session metadata |
| `feature:{farm_plot_id}` | 3600s (1 hour) | Materialized soil feature vectors for inference |
| `rate_limit:{ip}:{endpoint}` | 60s | Kong rate limit window counters |
| `reco:{user_id}:latest` | 1800s | Latest recommendation result cache |
| `weather:{lat}:{lon}` | 1800s | OpenWeatherMap API response cache |

---

## 4. JanusGraph Property Graph

### 4.1 Vertex Types (Labels)

| Vertex Label | Description | Key Properties |
| :--- | :--- | :--- |
| Crop | Crop entity | code, name, scientificName, seasonType, durationDays, waterRequirementMm, mspInrPerQuintal |
| CropVariety | Crop variety sub-entity | varietyCode, cropCode, yieldPotentialKgHa |
| Pest | Pest entity | pestCode, name, category, symptoms |
| Disease | Disease entity | code, name, severity, modelClassLabel |
| Chemical | Pesticide/fertilizer | code, name, activeIngredient, formulation, doseKgHa, isOrganic |
| SoilProfile | Soil type template | textureClass, phMin, phMax, organicCarbonPct |
| AgroEcoZone | Agro-ecological zone | zoneCode, region, rainfallAvgMm, name |
| Advisory | Advisory rule node | code, name, description, category |

### 4.2 Edge Types (Labels)

| Edge Label | From → To | Properties |
| :--- | :--- | :--- |
| SUSCEPTIBLE_TO | Crop → Pest/Disease | probability, severity |
| TREATS | Chemical → Pest/Disease | efficacy, doseKgHa, waitingPeriodDays |
| COMPATIBLE_WITH | Crop → Crop | benefitType, compatibilityScore |
| GROWS_BEST_IN | Crop → SoilProfile | suitabilityScore |
| AFFECTS | AgroEcoZone → Crop | rainfallAdequacy, temperatureSuitability |
| ROTATES_WITH | Crop → Crop | rotationBenefit |
| CONTROLS | Advisory → Pest/Disease | controlEfficacy |
| HAS_VARIETY | Crop → CropVariety | |

### 4.3 Graph Indexes

- **Composite Index:** `nameIndex` on name property (all vertex labels)
- **Mixed Index (JanusSearch):** `globalSearch` on name, description (Elasticsearch-backed full-text)
- **Vertex Label Index:** `cropByCode` on `code` property for Crop vertices
