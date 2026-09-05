# Administrator Manual
## AgriDecision AI — System Administration & Operations Guide
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Introduction & Responsibilities

The Platform Administrator is responsible for managing system access, monitoring infrastructure health, managing secrets in HashiCorp Vault, tracking AI model drift, configuring alerting thresholds, and handling security compliance requests (GDPR).

---

## 2. Admin Dashboard & Governance

### 2.1 Accessing the Admin Console

1. Log in to the Agronomist Portal: `https://app.agridecision.ai`
2. Ensure your user role is `ADMIN` or `SUPER_ADMIN`
3. Click **System Admin** in the bottom left of the sidebar navigation.

### 2.2 User Management & RBAC Provisioning

- **Promoting a User Role:**
  1. Go to **Admin → User Management**
  2. Search for user by phone number or email
  3. Select **Edit Role** and pick from: `FARMER`, `AGRONOMIST`, `ENTERPRISE`, `ADMIN`, `SUPER_ADMIN`
  4. Click **Save Role** — takes effect immediately for new requests.
- **Account Suspension:**
  - Click **Deactivate User** to set `is_active = False`. Active JWT sessions are revoked via Redis blacklist.
- **GDPR Compliance Actions:**
  - **Data Export:** Click **Export User Data (GDPR)** to download a JSON bundle of all stored records.
  - **Account Deletion:** Click **Anonymize & Delete User** to overwrite PII (name, phone, email) with irreversible hashes.

---

## 3. Observability & Monitoring (LGTM Stack)

### 3.1 Prometheus Metrics Monitoring

Access Prometheus at `https://prometheus.agridecision.ai` or via Grafana dashboards.

**Key Metrics to Monitor:**
- `http_requests_total{status=~"5.."}` — Tracks server error rate across all microservices (Alert threshold: > 1% in 5 min)
- `http_request_duration_seconds_bucket` — API latency metrics (p95 threshold: > 100 ms)
- `triton_model_inference_latency_microseconds` — AI inference execution time per model
- `model_drift_score{model="...", feature="..."}` — KS/PSI feature drift metrics (Alert threshold: > 0.25)
- `kafka_consumergroup_lag` — Telemetry queue processing delay

### 3.2 Grafana Dashboards Overview

Access Grafana at `https://grafana.agridecision.ai` (Default credentials: Admin managed).

1. **System Health & RED Metrics:** Overall request rate, error rate, and duration for all 9 microservices.
2. **AI Inference & Drift Telemetry:** Real-time performance of Triton inference server, ONNX runtimes, and KS/PSI distribution shifts.
3. **Database & Cache Health:** PostgreSQL connection pool saturation, TimescaleDB hypertable chunk counts, and Redis cache hit ratio (target > 95%).
4. **IoT & Event Ingestion:** Kafka topic throughput, sensor payload validation rate, and MQTT bridge status.

### 3.3 Log Aggregation with Loki

Log queries via Grafana Explore (Datasource: Loki):
```logql
# View all errors in advisory service
{app="advisory_service"} |= "ERROR"

# View Triton fallback events
{app="advisory_service"} |= "fallback_used"

# View authentication failures
{app="user_service"} |= "INVALID_OTP"
```

---

## 4. HashiCorp Vault Administration

### 4.1 Vault Unsealing & Status Check

```bash
# Check Vault status
vault status -address=https://vault.agridecision.ai

# Unseal Vault (requires 3 of 5 shamir keys if unsealed manually)
vault operator unseal -address=https://vault.agridecision.ai <unseal_key_1>
vault operator unseal -address=https://vault.agridecision.ai <unseal_key_2>
vault operator unseal -address=https://vault.agridecision.ai <unseal_key_3>
```

### 4.2 Key Rotation Procedures

- **Rotating Database Credentials:**
  1. Update target password in PostgreSQL: `ALTER USER agri_user WITH PASSWORD 'new_secret_pass';`
  2. Put updated credentials in Vault:
     `vault kv put kv/data/agri/database url="postgresql+asyncpg://agri_user:new_secret_pass@agri-postgres:5432/agri_db"`
  3. Restart backend pods: `kubectl rollout restart deployment -n agridecision-prod`
- **Rotating JWT RS256 Key Pair:**
  1. Generate new RSA 2048-bit key pair: `openssl genrsa -out private.pem 2048`
  2. Update key pair in Vault under `kv/data/agri/jwt`
  3. Update Kong JWT plugin public key registry.

---

## 5. Model Lifecycle & Registry Management

### 5.1 Inspecting Model Registry

Run Python CLI utility to view currently registered production models:
```bash
python -c "
from ai_services.model_registry.registry import ModelRegistryManager
mgr = ModelRegistryManager()
for m in mgr.list_all_versions():
    print(f'Model: {m[\"name\"]} | Ver: {m[\"version\"]} | Status: {m[\"status\"]}')
"
```

### 5.2 Promoting a Staging Model to Production

```python
from ai_services.model_registry.registry import ModelRegistryManager
mgr = ModelRegistryManager()
# Promote version 1.1.0 of crop_recommendation_v1
mgr.promote_model_version(name="crop_recommendation_v1", version="1.1.0", target_status="production")
```

---

## 6. Backup & Disaster Recovery

### 6.1 PostgreSQL + PostGIS Backup

```bash
# Trigger pg_dump backup
docker exec agri-postgres pg_dump -U agri_user -F c -b -v -f /backups/agri_db_$(date +%Y%m%d_%H%M%S).dump agri_db

# Upload to S3 Glacier
aws s3 cp /backups/ s3://agri-backups-production/postgres/ --recursive
```

### 6.2 TimescaleDB Hypertable Backup

```bash
# Backup hypertable schema and data using pg_dump
docker exec agri-timescaledb pg_dump -U agri_user -F c -d agri_timeseries -f /backups/timeseries_$(date +%Y%m%d).dump
```

### 6.3 Disaster Recovery RPO/RTO Targets

- **Recovery Point Objective (RPO):** < 1 hour (Automated hourly WAL archiving to S3)
- **Recovery Time Objective (RTO):** < 30 minutes (Automated Kubernetes recreate via ArgoCD + DB restore)
