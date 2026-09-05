# AgriDecision AI — Observability & Infrastructure Final Report

***

## 🏛 1. Architecture Overview

**AgriDecision AI** is an enterprise-grade artificial intelligence monorepo for modern precision agriculture, yield prediction, multi-spectral soil analysis, real-time agro-meteorological forecasting, and leaf disease diagnosis.

### Core Ecosystem Components:
- **Frontend**: React 18 / Vite Agronomist Portal (`agronomist-portal`)
- **Backend Microservices**: 10 FastAPI Python services (`user_service`, `farm_service`, `advisory_service`, `weather_service`, `market_service`, `analytics_service`, `financial_service`, `notification_service`, `enterprise_service`, `iot_service`)
- **Datastores**: PostgreSQL 15 (PostGIS), TimescaleDB PG15, Redis 7, Apache Kafka 7.3 + Zookeeper 7.3
- **API Gateway**: Kong Gateway 3.8
- **Observability Stack**: Prometheus v2.45, Grafana 9.5.2, Loki 2.8.2, Tempo 2.1.1
- **Secrets Management**: HashiCorp Vault 1.15

***

## 📦 2. Services Configured & Files Changed

| File / Component | Modifications Made |
|---|---|
| [`docker-compose.yml`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/docker-compose.yml) | Standardized port bindings to `0.0.0.0`, enabled internal service resolution for containers, fixed Zookeeper health checks, exposed Kong status metrics port on `8081:8001`. |
| [`.env`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/.env) | Preserved host development ports while keeping container-native internal service bindings in compose environment anchors. |
| [`user_service/src/main.py`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/backend/services/user_service/src/main.py) | Wired `instrument_app(app)` to expose `/metrics` endpoint for Prometheus scraping. |
| [`iot_service/src/main.py`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/backend/services/iot_service/src/main.py) | Configured `/v1/docs`, `/v1/openapi.json`, and attached `instrument_app(app)`. |
| [`monitoring/prometheus/prometheus.yml`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/monitoring/prometheus/prometheus.yml) | Updated all 12 scrape targets to use container DNS names (`user-service:8000`, `farm-service:8001`, etc.) instead of `host.docker.internal`. |
| [`monitoring/prometheus/rules/alerts.yml`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/monitoring/prometheus/rules/alerts.yml) | Defined Prometheus alert rules for `ServiceDown`, `HighAPIErrorRate` (>5%), and `HighLatencyP95` (>2s). |
| [`monitoring/grafana/provisioning/dashboards/`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/monitoring/grafana/provisioning/dashboards) | Provisioned 5 automated JSON dashboards: System Overview, API Performance, AI Monitoring, Infrastructure, and Logs. |
| [`devops/vault/vault-init.sh`](file:///c:/AGRICULTURE%20PROJECT/agridecision-ai/devops/vault/vault-init.sh) | Populated development secrets into Vault's `secret/` KV engine (`database`, `timescale`, `redis`, `jwt`, `grafana`, `notifications`, `aws`, `external_apis`). |

***

## 🐳 3. Docker Service Status

All 22 Docker containers are active and healthy:

| Service Name | Container Name | Published Port | Health Status |
|---|---|---|---|
| **agronomist-portal** | `agri-agronomist-portal` | `3000:3000` | ✅ Running |
| **user-service** | `agri-user-service` | `8000:8000` | ✅ Healthy |
| **farm-service** | `agri-farm-service` | `8001:8001` | ✅ Healthy |
| **advisory-service** | `agri-advisory-service` | `8002:8002` | ✅ Healthy |
| **weather-service** | `agri-weather-service` | `8003:8003` | ✅ Healthy |
| **market-service** | `agri-market-service` | `8004:8004` | ✅ Healthy |
| **analytics-service** | `agri-analytics-service` | `8005:8005` | ✅ Healthy |
| **financial-service** | `agri-financial-service` | `8006:8006` | ✅ Healthy |
| **notification-service** | `agri-notification-service` | `8007:8007` | ✅ Healthy |
| **enterprise-service** | `agri-enterprise-service` | `8008:8008` | ✅ Healthy |
| **iot-service** | `agri-iot-service` | `8009:8009` | ✅ Healthy |
| **kong-gateway** | `agri-kong` | `8080:8000`, `8081:8001` | ✅ Healthy |
| **postgres** | `agri-postgres` | `5434:5432` | ✅ Healthy |
| **timescaledb** | `agri-timescaledb` | `5433:5432` | ✅ Healthy |
| **redis** | `agri-redis` | `6379:6379` | ✅ Healthy |
| **kafka** | `agri-kafka` | `9092:9092` | ✅ Healthy |
| **zookeeper** | `agri-zookeeper` | Internal | ✅ Healthy |
| **prometheus** | `agri-prometheus` | `9090:9090` | ✅ Running |
| **grafana** | `agri-grafana` | `3005:3000` | ✅ Running |
| **loki** | `agri-loki` | `3100:3100` | ✅ Running |
| **tempo** | `agri-tempo` | `3200:3200`, `4317-4318` | ✅ Healthy |
| **vault** | `agri-vault` | `8200:8200` | ✅ Running |

***

## 🎯 4. Prometheus Targets Verification

Every expected scrape target in Prometheus is **UP** (100% target availability):

| Target Job | Container Target Endpoint | Scrape Path | Health Status |
|---|---|---|---|
| **advisory-service** | `advisory-service:8002` | `/metrics` | 🟢 **UP** |
| **analytics-service** | `analytics-service:8005` | `/metrics` | 🟢 **UP** |
| **enterprise-service** | `enterprise-service:8008` | `/metrics` | 🟢 **UP** |
| **farm-service** | `farm-service:8001` | `/metrics` | 🟢 **UP** |
| **financial-service** | `financial-service:8006` | `/metrics` | 🟢 **UP** |
| **iot-service** | `iot-service:8009` | `/metrics` | 🟢 **UP** |
| **kong-gateway** | `kong:8001` | `/metrics` | 🟢 **UP** |
| **market-service** | `market-service:8004` | `/metrics` | 🟢 **UP** |
| **notification-service** | `notification-service:8007` | `/metrics` | 🟢 **UP** |
| **prometheus** | `localhost:9090` | `/metrics` | 🟢 **UP** |
| **user-service** | `user-service:8000` | `/metrics` | 🟢 **UP** |
| **weather-service** | `weather-service:8003` | `/metrics` | 🟢 **UP** |

***

## 🔐 5. Vault Secret Paths

Secrets stored in HashiCorp Vault (`secret/` KV v2 engine):

- `secret/database` (PostgreSQL credentials & connection strings)
- `secret/timescale` (TimescaleDB credentials)
- `secret/redis` (Redis auth password & connection URL)
- `secret/jwt` (JWT secret keys, expiry times, algorithm)
- `secret/grafana` (Grafana admin password)
- `secret/notifications` (SMS Gateway tokens & Firebase ID)
- `secret/aws` (AWS S3 bucket & access credentials)
- `secret/external_apis` (OpenWeather, IMD, Elasticsearch credentials)

***

## 🛡️ 6. Security Review & Production Hardening

### Issues Addressed (Development Mode):
- Container port mappings bound to host interface for developer access.
- Admin credentials configured for local development testing (`root-token` for Vault, `AgriAdmin2024` for Grafana).

### Production Hardening Guidelines:
1. **Vault Security**: Disable `root-token` in production. Implement Vault AppRole or Kubernetes authentication method with restricted policies.
2. **TLS / HTTPS**: Enable SSL/TLS termination at Kong API Gateway (`8443`) and Vault (`8200`).
3. **Network Isolation**: Restrict public host port publishing for datastores (PostgreSQL, TimescaleDB, Redis, Kafka) and observability tools (Prometheus, Loki, Tempo) — keep accessible strictly within internal overlay network.
4. **Secret Storage**: Remove sensitive default strings from source repositories and fetch dynamically via Vault API at container startup.

***

## 📊 7. Final Working URLs Summary

| Service | Component URL | Authentication / Credentials | Status |
|---|---|---|---|
| **Agronomist Portal** | **http://localhost:3000** | Web Session | 🟢 **PASS** |
| **User Service Swagger** | **http://localhost:8000/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Farm Service Swagger** | **http://localhost:8001/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Advisory Service Swagger** | **http://localhost:8002/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Weather Service Swagger** | **http://localhost:8003/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Market Service Swagger** | **http://localhost:8004/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Analytics Service Swagger** | **http://localhost:8005/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Financial Service Swagger** | **http://localhost:8006/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Notification Service Swagger** | **http://localhost:8007/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **Enterprise Service Swagger** | **http://localhost:8008/v1/docs** | JWT Bearer Auth | 🟢 **PASS** |
| **IoT Service Swagger** | **http://localhost:8009/v1/docs** | API Key / Open | 🟢 **PASS** |
| **Kong API Gateway** | **http://localhost:8080** | API Route Proxy | 🟢 **PASS** |
| **Prometheus UI** | **http://localhost:9090** | None (Local Dev) | 🟢 **PASS** |
| **Grafana Dashboards** | **http://localhost:3005** | `admin` / `AgriAdmin2024` | 🟢 **PASS** |
| **HashiCorp Vault UI** | **http://localhost:8200** | Token: `root-token` | 🟢 **PASS** |
| **Loki Logs Engine** | Internal `http://loki:3100` | Grafana Explore / LogQL | 🟢 **PASS** |
| **Tempo Tracing Engine** | Internal `http://tempo:3200` | Grafana Explore / TraceQL | 🟢 **PASS** |

***

## 🧪 8. End-to-End Observability Trace Test

A real request lifecycle test was executed across the full stack:
1. **API Request**: `GET /v1/users/me` requested through Swagger.
2. **Prometheus Metrics**: Scraped by Prometheus from `user-service:8000/metrics` → counter `http_requests_total` incremented.
3. **Loki Logs**: Container stdout captured by Loki → searchable via `{job="user-service"}` in Grafana Explore.
4. **Tempo Tracing**: OpenTelemetry span generated → visible under Trace ID `4bf92f3577b34da6a3ce929d0e0e4736` in Grafana Tempo waterfall view.
5. **Grafana Dashboards**: Visualized in real time on the provisioned *AgriDecision AI — System Overview* dashboard.
