# Unified Modeling Language (UML) Diagrams
## AgriDecision AI — Complete System Design Visualizations
**Document Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Use Case Diagram

```mermaid
graph TD
    Farmer((Farmer))
    Agronomist((Certified Agronomist))
    Enterprise((Enterprise User))
    Admin((Platform Admin))

    subgraph AgriDecision_AI_System["AgriDecision AI System Boundary"]
        UC1[UC-1: Register & Verify via OTP]
        UC2[UC-2: Draw Farm Plot Boundary]
        UC3[UC-3: Upload Soil Test Profile]
        UC4[UC-4: Request AI Crop Recommendation]
        UC5[UC-5: Capture Leaf Image & Detect Disease]
        UC6[UC-6: View 7-Day Weather & ET₀ Forecast]
        UC7[UC-7: Check Mandi Prices & Forecasts]
        UC8[UC-8: Apply for Agri Credit & Loans]
        UC9[UC-9: Review & Annotate AI Recommendations]
        UC10[UC-10: Issue Custom Agronomic Advisory]
        UC11[UC-11: Create Procurement Contract]
        UC12[UC-12: Trace Supply Chain Origins]
        UC13[UC-13: Manage User Roles & Permissions]
        UC14[UC-14: Monitor System Telemetry & Model Drift]
        UC15[UC-15: Trigger GDPR Data Export / Deletion]
    end

    Farmer --> UC1
    Farmer --> UC2
    Farmer --> UC3
    Farmer --> UC4
    Farmer --> UC5
    Farmer --> UC6
    Farmer --> UC7
    Farmer --> UC8

    Agronomist --> UC1
    Agronomist --> UC4
    Agronomist --> UC5
    Agronomist --> UC9
    Agronomist --> UC10

    Enterprise --> UC1
    Enterprise --> UC11
    Enterprise --> UC12

    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
```

---

## 2. Class Diagram (Backend Core Domain)

```mermaid
classDiagram
    class User {
        +UUID id
        +String phone_number
        +String email
        +String full_name
        +Role role
        +Boolean is_active
        +request_otp()
        +verify_otp()
    }

    class FarmPlot {
        +UUID id
        +UUID owner_id
        +String name
        +Decimal total_area_ha
        +String irrigation_type
        +Decimal centroid_lat
        +Decimal centroid_lng
        +get_boundary()
        +get_soil_profile()
    }

    class SoilProfile {
        +UUID id
        +UUID plot_id
        +Decimal ph_level
        +Decimal organic_carbon_pct
        +Decimal nitrogen_content
        +Decimal phosphorus_content
        +Decimal potassium_content
        +validate_bounds()
    }

    class Recommendation {
        +UUID id
        +UUID plot_id
        +String recommended_crop
        +Decimal confidence_score
        +JSON shap_values
        +Boolean fallback_used
    }

    class TritonInferenceClient {
        +String triton_url
        +infer_crop_recommendation(vector)
        +infer_disease_detection(image)
    }

    User "1" -- "*" FarmPlot : owns
    FarmPlot "1" -- "1" SoilProfile : has
    FarmPlot "1" -- "*" Recommendation : evaluated_in
    Recommendation ..> TritonInferenceClient : calls
```

---

## 3. Activity Diagram (Crop Recommendation Flow)

```mermaid
stateDiagram-v2
    [*] --> SoilProfileSubmitted
    SoilProfileSubmitted --> ValidateSoilBounds
    ValidateSoilBounds --> BoundsValid: Soil Values Within Limits
    ValidateSoilBounds --> RejectInput: Values Out of Bounds
    RejectInput --> [*]

    BoundsValid --> CheckRedisCache
    CheckRedisCache --> CacheHit: Feature Vector Cached
    CheckRedisCache --> BuildFeatureVector: Cache Miss
    BuildFeatureVector --> CheckTritonAvailable

    CacheHit --> CheckTritonAvailable

    CheckTritonAvailable --> InvokeTriton: Triton Server Healthy
    CheckTritonAvailable --> InvokeRuleEngine: Triton Unavailable / Down

    InvokeTriton --> ComputeSHAP
    InvokeRuleEngine --> MarkFallbackUsed

    ComputeSHAP --> StoreRecommendation
    MarkFallbackUsed --> StoreRecommendation

    StoreRecommendation --> PublishKafkaEvent
    PublishKafkaEvent --> ReturnAPIResponse
    ReturnAPIResponse --> [*]
```

---

## 4. Sequence Diagram (Disease Detection & Advisory Flow)

```mermaid
sequenceDiagram
    actor Farmer
    participant App as Mobile App
    participant Kong as Kong Gateway
    participant AdvSvc as advisory_service
    participant ResNet as ResNet-50 CNN (Triton)
    participant GradCam as Grad-CAM Generator
    participant Kafka as Kafka Cluster
    participant Notif as notification_service

    Farmer->>App: Take Leaf Photo & Click Analyze
    App->>Kong: POST /v1/diagnosis/disease-detection (multipart)
    Kong->>AdvSvc: Authenticate & Route Request
    AdvSvc->>ResNet: Execute CNN Inference (224x224 RGB)
    ResNet-->>AdvSvc: Prediction: "Leaf Rust" (Confidence: 94%)
    AdvSvc->>GradCam: Generate Layer-4 Attention Heatmap
    GradCam-->>AdvSvc: Return Heatmap Image & Overlay S3 URL
    AdvSvc->>Kafka: Publish "disease.detected" Event
    Kafka-->>Notif: Trigger Push Notification Alert
    AdvSvc-->>App: Return Diagnosis, Grad-CAM URL & Treatment Steps
    App-->>Farmer: Display Diagnosis + Visual Heatmap
```

---

## 5. Deployment Diagram

```mermaid
graph TB
    subgraph Client_Devices["Client Hardware"]
        MobileDevice["Android / iOS Device<br/>(Flutter App + SQLite)"]
        Browser["Desktop Browser<br/>(React Web App)"]
    end

    subgraph Cloud_Infrastructure["AWS EKS Cloud Infrastructure"]
        subgraph Ingress_Node["Ingress Layer"]
            KongGW["Kong API Gateway Pod<br/>(Port 8000 / TLS 1.3)"]
        end

        subgraph Worker_Nodes["EKS Worker Nodes"]
            ServicePods["9 FastAPI Microservice Deployments<br/>(2+ Replicas per Service)"]
            TritonPod["NVIDIA Triton Inference Server<br/>(ONNX Runtime Engine)"]
            VaultPod["HashiCorp Vault Secrets Pod"]
        end

        subgraph Managed_Data["AWS Managed Data Services"]
            RDS[("Amazon RDS PostgreSQL + PostGIS")]
            Timescale[("TimescaleDB Hypertables")]
            ElastiCache[("Amazon ElastiCache Redis")]
            MSK[("Amazon MSK Kafka Cluster")]
        end
    end

    MobileDevice --> KongGW
    Browser --> KongGW
    KongGW --> ServicePods
    ServicePods --> TritonPod
    ServicePods -.-> VaultPod
    ServicePods --> RDS
    ServicePods --> Timescale
    ServicePods --> ElastiCache
    ServicePods --> MSK
```
