# API Documentation
## AgriDecision AI — Complete REST API Reference
**Base URL:** `https://api.agridecision.ai` (Production) | `http://localhost:8000` (Local via Kong)  
**API Version:** v1 | **Auth:** Bearer JWT (RS256)

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## user_service API (Port 8001)

### POST /v1/auth/request-otp
Request an OTP for phone-number-based login/registration.

**Request Body:**
```json
{ "phone_number": "+919876543210" }
```
**Response 200:**
```json
{ "message": "OTP sent successfully", "debug_otp": "482930" }
```

---

### POST /v1/auth/verify-otp
Verify OTP and receive JWT access + refresh token pair.

**Request Body:**
```json
{
  "phone_number": "+919876543210",
  "otp_code": "482930",
  "device_fingerprint": "abc123"
}
```
**Response 200 (TokenResponse):**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "FARMER",
    "full_name": "Ramesh Kumar"
  }
}
```

---

### POST /v1/auth/oauth/google
Authenticate via Google OAuth2 ID Token.

**Request Body:**
```json
{ "id_token": "google_id_token_string", "device_fingerprint": "abc123" }
```
**Response 200:** Same as `verify-otp` → TokenResponse

---

### POST /v1/auth/mfa/setup
Generate TOTP secret and provisioning QR code URL.

**Headers:** Bearer token required  
**Response 200 (MFASetupResponse):**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "otpauth_url": "otpauth://totp/AgriDecision:+919876543210?secret=JBSWY3DPEHPK3PXP&issuer=AgriDecision",
  "qr_code_url": "https://chart.googleapis.com/chart?chs=200x200&..."
}
```

---

### POST /v1/auth/mfa/verify
Verify TOTP code for MFA validation.

**Request Body:** `{ "totp_code": "123456" }`  
**Response 200:** `{ "verified": true }`

---

### POST /v1/users/
Create user profile.

**Request Body:**
```json
{
  "full_name": "Ramesh Kumar",
  "phone_number": "+919876543210",
  "email": "ramesh@example.com",
  "role": "FARMER",
  "state": "Telangana",
  "district": "Medak"
}
```
**Response 201:** UserResponse object

---

### GET /v1/users/{user_id}
Get user profile by UUID.

**Response 200:**
```json
{
  "id": "550e8400-...",
  "full_name": "Ramesh Kumar",
  "phone_number": "+919876543210",
  "role": "FARMER",
  "is_active": true,
  "created_at": "2026-06-01T10:30:00Z"
}
```

---

### GET /v1/users/{user_id}/gdpr-export
Export all personal data for GDPR compliance. Admin or self only.

**Response 200:**
```json
{
  "user": {...},
  "farm_plots": [...],
  "recommendations": [...],
  "loan_applications": [...],
  "audit_logs": [...]
}
```

---

### DELETE /v1/users/{user_id}
GDPR data deletion — anonymizes PII fields. Admin only.

**Response 204:** No content.

---

## farm_service API (Port 8002)

### POST /v1/farms/
Create a new farm plot.

**Request Body:**
```json
{
  "name": "Green Acres Plot 1",
  "total_area_ha": 2.5,
  "irrigation_type": "DRIP",
  "centroid_lat": 17.3850,
  "centroid_lng": 78.4867
}
```
**Response 201:**
```json
{
  "id": "6ba7b810-...",
  "name": "Green Acres Plot 1",
  "total_area_ha": "2.5000",
  "irrigation_type": "DRIP",
  "owner_id": "550e8400-...",
  "created_at": "2026-07-28T10:00:00Z"
}
```

---

### GET /v1/farms/{farm_id}
Get farm plot with associated boundary, soil profile, and seasons.

**Response 200:**
```json
{
  "id": "6ba7b810-...",
  "name": "Green Acres Plot 1",
  "total_area_ha": "2.5000",
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[78.48, 17.38], [78.49, 17.38], [78.49, 17.39], [78.48, 17.39], [78.48, 17.38]]]
  },
  "soil_profile": {
    "ph_level": "6.80",
    "nitrogen_content": "180.00",
    "phosphorus_content": "45.00",
    "potassium_content": "220.00"
  }
}
```

---

### PUT /v1/farms/{farm_id}/boundary
Update farm boundary as GeoJSON polygon.

**Request Body:**
```json
{
  "type": "Polygon",
  "coordinates": [[[78.48, 17.38], [78.49, 17.38], ...]]
}
```
**Response 200:** Updated boundary object

---

### POST /v1/farms/{farm_id}/soil
Upload or update soil profile for a farm plot.

**Request Body:**
```json
{
  "ph_level": 6.8,
  "organic_carbon_pct": 1.2,
  "nitrogen_content": 180.0,
  "phosphorus_content": 45.0,
  "potassium_content": 220.0,
  "electrical_conductivity": 0.35,
  "texture_class": "SANDY_LOAM"
}
```
**Response 200:**
```json
{
  "soil_profile": {...},
  "validation_report": {
    "is_valid": true,
    "violations": []
  }
}
```

---

### GET /v1/parcels/nearby
Spatial query — find farm plots within radius.

**Query Params:** `?lat=17.38&lng=78.48&radius_km=25&limit=20`  
**Response 200:** Array of nearby farm plot objects with distance_km field.

---

## advisory_service API (Port 8003)

### POST /v1/diagnosis/crop-recommendation
Get AI crop recommendation from soil profile.

**Request Body:**
```json
{
  "plot_id": "6ba7b810-...",
  "override_features": {
    "ph_level": 6.8,
    "nitrogen_content": 180.0
  }
}
```
**Response 200:**
```json
{
  "recommended_crop": "wheat",
  "confidence": 0.79,
  "crop_index": 3,
  "all_probabilities": {
    "rice": 0.02, "maize": 0.05, "wheat": 0.79, "cotton": 0.04
  },
  "shap_values": {
    "ph_level": 0.18, "nitrogen_content": 0.22, "rainfall_mm": 0.15,
    "potassium_content": 0.12, "temperature_c": 0.14, "phosphorus_content": 0.10, "organic_carbon": 0.09
  },
  "fallback_used": false,
  "model_version": "1.0.0"
}
```

---

### POST /v1/diagnosis/disease-detection
Detect crop leaf disease from uploaded image.

**Content-Type:** `multipart/form-data`  
**Form fields:**
- `image`: JPEG/PNG file (max 5MB)
- `crop_type`: str (e.g., "wheat")
- `plot_id`: UUID (optional)

**Response 200:**
```json
{
  "diagnosis_id": "8f14e45f-...",
  "predicted_class": "healthy",
  "confidence": 0.94,
  "all_classes": {
    "healthy": 0.94, "leaf_rust": 0.04, "powdery_mildew": 0.02
  },
  "gradcam_url": "https://s3.amazonaws.com/agri-uploads/gradcam/8f14e45f.jpg",
  "remedy_steps": [],
  "model_version": "1.0.0"
}
```

---

### POST /v1/diagnosis/advisory-query
Natural language agronomic advisory query.

**Request Body:**
```json
{
  "query": "Yellow leaves on wheat crop after rain",
  "soil_profile": { "ph_level": 6.8, "nitrogen_content": 180 },
  "weather_snapshot": { "temp_max_c": 31.0, "precipitation_mm": 120.0 }
}
```
**Response 200:**
```json
{
  "diagnosis": "Soil pH is 6.8. Nitrogen level is 180 kg/ha. Probable nitrogen deficiency or waterlogging stress.",
  "remedy_steps": [
    "Conduct drainage assessment for waterlogging.",
    "Apply Urea at 60 kg/ha in split dose.",
    "Monitor pH weekly. Apply lime if below 5.5."
  ],
  "warning_signs": ["Yellowing of leaf tips", "Sudden wilting during midday"],
  "crop_suitability": [
    { "crop_name": "wheat", "suitability_score": 0.88, "reason": "Optimal pH for wheat is 6.0-7.0" }
  ]
}
```

---

## iot_service API (Port 8004)

### POST /v1/iot/devices
Register an IoT sensor device.

**Request Body:**
```json
{
  "plot_id": "6ba7b810-...",
  "device_type": "SOIL_SENSOR",
  "serial_number": "AGR-SS-00421",
  "firmware_version": "2.3.1"
}
```
**Response 201:** Device registration object with `device_id`.

---

### POST /v1/iot/telemetry
Ingest sensor reading (also accepts MQTT-bridged payloads).

**Request Body:**
```json
{
  "device_id": "...",
  "timestamp": "2026-07-28T15:00:00Z",
  "soil_temp_c": 24.5,
  "soil_moisture_pct": 38.2,
  "conductivity_ds_m": 0.42,
  "battery_voltage": 3.7
}
```
**Response 201:** `{ "accepted": true, "timestamp": "2026-07-28T15:00:00Z" }`

---

## market_service API (Port 8005)

### GET /v1/market/prices
Get current commodity prices.

**Query Params:** `?commodity=wheat&state=Telangana&limit=10`  
**Response 200:**
```json
{
  "prices": [
    {
      "commodity": "wheat",
      "mandi": "Sangareddy APMC",
      "min_price_inr": 2150,
      "max_price_inr": 2280,
      "modal_price_inr": 2200,
      "date": "2026-07-28"
    }
  ]
}
```

---

### GET /v1/market/forecast/{commodity}
Get 7-day price forecast from LSTM model.

**Response 200:**
```json
{
  "commodity": "wheat",
  "forecast": [
    { "date": "2026-07-29", "predicted_price_inr": 2215 },
    { "date": "2026-07-30", "predicted_price_inr": 2228 },
    ...
  ],
  "model_version": "1.0.0",
  "confidence_interval_95": [2190, 2270]
}
```

---

## weather_service API (Port 8006)

### GET /v1/weather/forecast
Get 7-day agrometeorological forecast for a plot.

**Query Params:** `?plot_id=6ba7b810-...`  
**Response 200:**
```json
{
  "plot_id": "6ba7b810-...",
  "forecast": [
    {
      "date": "2026-07-28",
      "temp_max_c": 31.0,
      "temp_min_c": 22.0,
      "rainfall_mm": 12.5,
      "humidity_pct": 78.0,
      "evapotranspiration_mm": 4.8,
      "uv_index": 7.2
    }
  ],
  "eto_method": "FAO56_PENMAN_MONTEITH"
}
```

---

## financial_service API (Port 8007)

### POST /v1/loans/apply
Submit agricultural loan application.

**Request Body:**
```json
{
  "purpose": "CROP_PRODUCTION",
  "amount_inr": 150000,
  "collateral_description": "2.5 hectare agricultural land",
  "plot_id": "6ba7b810-..."
}
```
**Response 201:**
```json
{
  "application_id": "...",
  "credit_score": 720,
  "status": "UNDER_REVIEW",
  "recommended_schemes": ["PM-KISAN Credit Card", "NABARD Short-term Crop Loan"]
}
```

---

## enterprise_service API (Port 8008)

### POST /v1/contracts/
Create procurement contract.

**Request Body:**
```json
{
  "commodity": "wheat",
  "quantity_mt": 50.0,
  "price_per_quintal_inr": 2200,
  "delivery_date": "2026-11-15",
  "linked_plot_ids": ["6ba7b810-..."]
}
```
**Response 201:** Contract object with contract_number.

---

## notification_service API (Port 8009)

### POST /v1/notifications/dispatch
Dispatch notification (internal service-to-service endpoint).

**Request Body:**
```json
{
  "user_id": "550e8400-...",
  "channel": "SMS",
  "template": "ADVISORY_READY",
  "variables": { "crop": "Wheat", "recommendation_id": "..." }
}
```
**Response 202:** `{ "queued": true, "notification_id": "..." }`
