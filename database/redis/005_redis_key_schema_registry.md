# ============================================================
# AgriDecision AI — Redis Key Schema Registry
# ============================================================
# This document defines ALL Redis key patterns, data structures,
# TTL policies, and serialization formats used across the platform.
# ============================================================
# Conventions:
#   - Namespaces use colon (:) as separator
#   - All keys are lowercase with underscores
#   - TTL = Time-To-Live in seconds (0 = no expiry)
#   - Data types: STRING, HASH, LIST, SET, SORTED_SET, JSON (RedisJSON)
# ============================================================

## 1. Authentication & Session Keys

### 1.1 OTP Cache
```
Key Pattern : otp:{phone_number}
Data Type   : STRING (6-digit code as plain string)
TTL         : 300 seconds (5 minutes)
Serialization: Plain string
Example     : otp:+919876543210  →  "482910"
Notes       : Written on OTP dispatch. Deleted on successful verification.
              After 3 failed attempts, key is replaced with lockout key.
```

### 1.2 OTP Lockout
```
Key Pattern : otp_lockout:{phone_number}
Data Type   : STRING (attempt count)
TTL         : 900 seconds (15 minutes)
Serialization: Plain integer string
Example     : otp_lockout:+919876543210  →  "3"
Notes       : INCR on each failed OTP attempt. API returns 429 when value >= 3.
```

### 1.3 JWT Refresh Token Blacklist
```
Key Pattern : token_blacklist:{refresh_token_hash}
Data Type   : STRING ("1" as flag)
TTL         : 2592000 seconds (30 days, matches refresh token expiry)
Serialization: Static value "1"
Example     : token_blacklist:sha256_hash_here  →  "1"
Notes       : Written on logout or forced session termination.
              Gateway checks this before accepting refresh requests.
```

### 1.4 Active User Session Index
```
Key Pattern : session:{user_id}:active_sessions
Data Type   : SET (set of session UUIDs)
TTL         : 0 (no expiry; managed by application on logout)
Serialization: UUID strings
Example     : session:usr_abc123  →  {sess_001, sess_002}
Notes       : Used for "terminate all sessions" / account suspension flows.
```

---

## 2. Feature Store — Online Feature Cache (Feast)

### 2.1 Farm Plot Feature Vector
```
Key Pattern : feast:plot_features:{farm_plot_id}
Data Type   : HASH
TTL         : 3600 seconds (1 hour, refreshed by Feast materialization)
Fields:
  soil_ph                → FLOAT (e.g. "6.80")
  soil_texture_class     → STRING (e.g. "CLAY_LOAM")
  organic_carbon_pct     → FLOAT
  nitrogen_kg_ha         → FLOAT
  phosphorus_kg_ha       → FLOAT
  potassium_kg_ha        → FLOAT
  area_hectares          → FLOAT
  aez_zone_code          → STRING
  irrigation_type        → STRING
  last_crop_code         → STRING
  last_yield_kg_ha       → FLOAT
  materialized_at        → ISO8601 timestamp
Example:
  feast:plot_features:plot_abc123 → {soil_ph: "6.80", texture_class: "CLAY_LOAM", ...}
```

### 2.2 Weather Feature Vector (Real-time Push Source)
```
Key Pattern : feast:weather_features:{farm_plot_id}
Data Type   : HASH
TTL         : 7200 seconds (2 hours)
Fields:
  temp_c_current         → FLOAT
  temp_c_7day_avg        → FLOAT
  rainfall_mm_7day_sum   → FLOAT
  eto_mm_yesterday       → FLOAT
  humidity_pct_current   → FLOAT
  drought_stress_index   → FLOAT (0–1)
  growing_degree_days    → FLOAT
  last_updated           → ISO8601 timestamp
```

### 2.3 Market Feature Vector
```
Key Pattern : feast:market_features:{crop_code}:{state_code}
Data Type   : HASH
TTL         : 86400 seconds (24 hours)
Fields:
  modal_price_inr_yesterday → FLOAT
  modal_price_7day_avg      → FLOAT
  modal_price_30day_avg     → FLOAT
  price_trend_direction     → STRING (UP/DOWN/STABLE)
  arrivals_7day_avg_tonnes  → FLOAT
  msp_inr_per_quintal       → FLOAT
```

---

## 3. Advisory Engine Cache

### 3.1 Crop Recommendation Cache
```
Key Pattern : advisory:rec:{farm_plot_id}:{season_label}
Data Type   : JSON (RedisJSON)
TTL         : 21600 seconds (6 hours)
Serialization: JSON blob of top-5 recommendation items
Example Value:
  {
    "recommendation_id": "rec_uuid",
    "generated_at": "2026-07-23T10:00:00Z",
    "model_version": "crop_selector_v3:3.1.0",
    "items": [
      {"rank": 1, "crop_code": "ZEA_MAYS", "probability": 0.89, "expected_yield": 5200},
      {"rank": 2, "crop_code": "SOYBEAN",  "probability": 0.76, "expected_yield": 1800}
    ]
  }
Notes: Cache-aside pattern. Advisory service populates on first miss.
       Invalidated when soil profile or weather features update.
```

### 3.2 Irrigation Schedule Cache
```
Key Pattern : advisory:irrigation:{farm_plot_id}:{date_iso}
Data Type   : HASH
TTL         : 86400 seconds (24 hours — refreshed nightly)
Fields:
  eto_mm             → FLOAT
  etc_mm             → FLOAT
  irrigation_required → "true" / "false"
  depth_mm           → FLOAT
  drip_runtime_mins  → FLOAT
```

### 3.3 Agronomist Queue Depth (for load balancing)
```
Key Pattern : advisory:agro_queue_depth:{agronomist_user_id}
Data Type   : STRING (integer count)
TTL         : 0 (persisted, decremented on review completion)
Example     : advisory:agro_queue_depth:usr_agro123  →  "12"
Notes       : INCR on new low-confidence diagnosis. DECR on agronomist review.
              Used by assignment service for load-balanced cohort allocation.
```

---

## 4. Rate Limiting (Kong Gateway + Application)

### 4.1 API Rate Limit Counter (Sliding Window)
```
Key Pattern : rate_limit:{api_key_id}:{window_timestamp_minute}
Data Type   : STRING (integer counter)
TTL         : 120 seconds (2x window size for safe cleanup)
Serialization: INCR atomic counter
Example     : rate_limit:key_abc:1721730000  →  "847"
Notes       : Kong plugin manages this. Hard limit enforced at gateway level.
```

### 4.2 User Request Rate Limit (Per Endpoint)
```
Key Pattern : rate_limit:user:{user_id}:{endpoint_group}:{window_minute}
Data Type   : STRING (integer counter)
TTL         : 120 seconds
Example     : rate_limit:user:usr_abc:diagnosis_upload:1721730000  →  "3"
Notes       : Endpoint groups: general, diagnosis_upload, voice_query
              Limits: general=100/min, diagnosis_upload=10/min, voice_query=20/min
```

---

## 5. Market Price Cache

### 5.1 Daily Mandi Price Summary
```
Key Pattern : market:prices:{state_code}:{crop_code}:{date_iso}
Data Type   : HASH
TTL         : 86400 seconds (24 hours)
Fields:
  mandi_count         → INTEGER
  avg_modal_price_inr → FLOAT
  min_price_inr       → FLOAT
  max_price_inr       → FLOAT
  total_arrivals_t    → FLOAT
  top_mandis          → JSON string (list of {mandi_code, modal_price_inr})
```

### 5.2 Price Forecast Cache
```
Key Pattern : market:forecast:{mandi_code}:{crop_code}:{horizon}
Data Type   : HASH
TTL         : 43200 seconds (12 hours)
Fields:
  q10_price_inr  → FLOAT
  q50_price_inr  → FLOAT
  q90_price_inr  → FLOAT
  generated_at   → ISO8601
  model_version  → STRING
```

---

## 6. Notification State

### 6.1 Device FCM Token Registry
```
Key Pattern : notify:fcm_token:{user_id}:{device_platform}
Data Type   : STRING (FCM registration token)
TTL         : 2592000 seconds (30 days; refreshed on app open)
Example     : notify:fcm_token:usr_abc:ANDROID  →  "fcm_abc123xyz..."
```

### 6.2 Notification Deduplication
```
Key Pattern : notify:dedup:{user_id}:{event_type}:{content_hash}
Data Type   : STRING ("sent" flag)
TTL         : 3600 seconds (1 hour — prevents duplicate alerts)
Notes       : content_hash = MD5 of notification body + event type.
              Skip delivery if key exists.
```

---

## 7. Distributed Locks (Redlock)

### 7.1 Plot Boundary Update Lock
```
Key Pattern : lock:plot_boundary:{farm_plot_id}
Data Type   : STRING (lock token UUID)
TTL         : 10 seconds (auto-release on crash)
Notes       : Acquired before writing PostGIS boundary geometry.
              Prevents concurrent boundary edits causing geometry corruption.
```

### 7.2 Diagnosis Processing Lock
```
Key Pattern : lock:diagnosis:{diagnosis_record_id}
Data Type   : STRING (lock token UUID)
TTL         : 60 seconds (Triton inference timeout)
Notes       : Prevents duplicate Triton inference calls for the same upload.
```

### 7.3 Payment Webhook Idempotency Lock
```
Key Pattern : lock:payment_webhook:{gateway_order_id}
Data Type   : STRING (lock token UUID)
TTL         : 30 seconds
Notes       : Ensures exactly-once processing of payment gateway webhooks.
```

---

## 8. Idempotency Key Store

### 8.1 API Idempotency Cache
```
Key Pattern : idempotency:{idempotency_key_uuid}
Data Type   : JSON (RedisJSON)
TTL         : 86400 seconds (24 hours per RFC spec)
Serialization:
  {
    "status": "COMPLETED",
    "response_status_code": 201,
    "response_body": { ... },
    "created_at": "2026-07-23T10:00:00Z"
  }
Endpoints using idempotency:
  - POST /v1/plots          (Idempotency-Key header required)
  - POST /v1/finance/loans/apply
  - POST /v1/subscriptions/purchase
  - POST /v1/advisory/diagnose
```

---

## 9. Telemetry & Platform Counters

### 9.1 Daily Active Users Counter
```
Key Pattern : metrics:dau:{date_iso}
Data Type   : SET (set of user UUIDs) — or HyperLogLog for large scale
TTL         : 172800 seconds (48 hours)
Notes       : SADD user_id on each authenticated API call.
              SCARD on day end for daily metric aggregation.
              Switch to PFADD (HyperLogLog) when DAU > 100,000.
```

### 9.2 Diagnosis Counter per User per Month
```
Key Pattern : metrics:diag_count:{user_id}:{year_month}
Data Type   : STRING (integer counter)
TTL         : 2678400 seconds (31 days)
Notes       : INCR on each submitted diagnosis.
              Read by subscription service to enforce monthly limits.
```

---

## 10. Redis Cluster Configuration Notes

| Parameter | Value | Rationale |
|---|---|---|
| **Mode** | Redis Cluster (6 nodes: 3 primary + 3 replica) | HA + horizontal sharding |
| **Keyspace Notification** | `KEA` (all events) | Enables TTL expiry hooks for OTP lockout automation |
| **Max Memory Policy** | `allkeys-lru` | Evict LRU keys under memory pressure (cache-safe) |
| **Max Memory** | 16GB per primary node | Sufficient for 10M active key-value pairs |
| **Persistence** | RDB every 900s + AOF `everysec` | Balance durability with write throughput |
| **Timeout** | 300 seconds (idle client disconnect) | Prevents stale connection accumulation |
| **Replication** | Synchronous to at least 1 replica | Prevents data loss on primary failure |
