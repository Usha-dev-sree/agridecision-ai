# Architecture Diagrams
## AgriDecision AI — System Architecture & Data Flow Visualizations
**Document Version:** 1.0 | **Date:** July 28, 2026

---

## 1. High-Level System Architecture Diagram

```mermaid
graph TD
    subgraph Clients["Clients & Edge Layer"]
        Mobile["Flutter 3 Mobile App<br/>(Offline SQLite, GPS, Camera)"]
        Web["React 18 Web Portal<br/>(Leaflet, Recharts, MUI)"]
        IoT["IoT Sensors / MQTT<br/>(Soil, Weather)"]
    end

    subgraph Security["Gateway & Security Layer"]
        Kong["Kong API Gateway (Port 8000)<br/>(TLS 1.3, RS256 JWT, Rate Limiting)"]
        Vault["HashiCorp Vault (Port 8200)<br/>(Secrets KV-v2 Engine)"]
    end

    subgraph Microservices["Backend Microservices Cluster (FastAPI)"]
        US["user_service<br/>(Port 8001)"]
        FS["farm_service<br/>(Port 8002)"]
        AS["advisory_service<br/>(Port 8003)"]
        IS["iot_service<br/>(Port 8004)"]
        MS["market_service<br/>(Port 8005)"]
        WS["weather_service<br/>(Port 8006)"]
        FIN["financial_service<br/>(Port 8007)"]
        ENT["enterprise_service<br/>(Port 8008)"]
        NS["notification_service<br/>(Port 8009)"]
    end

    subgraph AI_Layer["AI Services & Inference Gateway"]
        Triton["NVIDIA Triton Inference Server<br/>(Port 8080)"]
        ONNX["ONNX Models<br/>(RF, GBR, ResNet-50, BiLSTM)"]
        XAI["XAI Module<br/>(SHAP & Grad-CAM)"]
        JG["JanusGraph Property Graph<br/>(450+ Knowledge Triples)"]
    end

    subgraph Data["Polyglot Data Layer"]
        PG[("PostgreSQL + PostGIS<br/>(Relational & Spatial Data)")]
        TS[("TimescaleDB<br/>(Hypertables & Continuous Aggregates)")]
        Redis[("Redis 7<br/>(Sessions & Feature Store)")]
        Kafka[("Apache Kafka<br/>(Event Streaming Mesh)")]
    end

    subgraph Observability["LGTM Observability Stack"]
        Prom["Prometheus"]
        Graf["Grafana"]
        Loki["Loki"]
        Tempo["Tempo"]
    end

    Mobile --> Kong
    Web --> Kong
    IoT --> IS

    Kong --> US
    Kong --> FS
    Kong --> AS
    Kong --> IS
    Kong --> MS
    Kong --> WS
    Kong --> FIN
    Kong --> ENT
    Kong --> NS

    Kong -.-> Vault

    US --> PG
    US --> Redis
    FS --> PG
    FS --> TS
    AS --> Triton
    AS --> JG
    AS --> XAI
    IS --> TS
    IS --> Kafka
    AS --> Kafka
    NS --> Kafka

    Triton --> ONNX

    Microservices -.-> Prom
    Microservices -.-> Loki
    Microservices -.-> Tempo
    Prom --> Graf
    Loki --> Graf
    Tempo --> Graf
```

---

## 2. Microservice Container & Network Topology Diagram

```mermaid
flowchart LR
    subgraph K8s_Cluster["Kubernetes Cluster: agridecision-prod"]
        subgraph Ingress_Namespace["Ingress & Gateway"]
            KongPod["Kong Ingress Controller"]
        end

        subgraph Service_Namespace["Application Pods (2+ Replicas Each)"]
            UserPod["user-service deployment"]
            FarmPod["farm-service deployment"]
            AdvPod["advisory-service deployment"]
            IotPod["iot-service deployment"]
            MarketPod["market-service deployment"]
            WeatherPod["weather-service deployment"]
            FinPod["financial-service deployment"]
            NotifPod["notification-service deployment"]
        end

        subgraph Data_Namespace["Datastore Pods / Managed Cloud Services"]
            PostgresPod[("PostgreSQL + PostGIS")]
            TimescalePod[("TimescaleDB Hypertables")]
            RedisPod[("Redis Cluster")]
            KafkaPod[("Apache Kafka + ZooKeeper")]
        end
    end

    KongPod --> UserPod
    KongPod --> FarmPod
    KongPod --> AdvPod
    KongPod --> IotPod
    KongPod --> MarketPod
    KongPod --> WeatherPod
    KongPod --> FinPod

    UserPod --> PostgresPod
    UserPod --> RedisPod
    FarmPod --> PostgresPod
    FarmPod --> TimescalePod
    AdvPod --> RedisPod
    IotPod --> TimescalePod
    IotPod --> KafkaPod
    NotifPod --> KafkaPod
```

---

## 3. End-to-End AI Advisory Data Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer (Mobile / Web)
    participant Gateway as Kong Gateway
    participant Advisory as advisory_service
    participant FarmSvc as farm_service
    participant Redis as Redis Feature Store
    participant Triton as Triton / ONNX Engine
    participant XAI as SHAP / Grad-CAM Explainer
    participant Kafka as Kafka Event Stream
    participant Notif as notification_service

    Farmer->>Gateway: POST /v1/diagnosis/crop-recommendation (plot_id)
    Gateway->>Gateway: Validate RS256 JWT & Rate Limit
    Gateway->>Advisory: Forward Authorized Request
    Advisory->>FarmSvc: GET /v1/farms/{plot_id}/soil
    FarmSvc-->>Advisory: Return Soil Profile (pH, N, P, K, OC%)
    Advisory->>Redis: Check Feature Store Cache
    Redis-->>Advisory: Feature Vector Ready
    Advisory->>Triton: POST /v2/models/crop_recommendation/infer
    Triton->>Triton: Run ONNX Random Forest Inference
    Triton-->>Advisory: Prediction (Recommended Crop: Wheat, Conf: 79%)
    Advisory->>XAI: Compute SHAP Attribution Values
    XAI-->>Advisory: SHAP Feature Importance Dictionary
    Advisory->>Kafka: Publish Event to "advisory.results" Topic
    Kafka-->>Notif: Consume Advisory Result
    Notif-->>Farmer: Send SMS / Push Notification
    Advisory-->>Farmer: Return JSON (Crop, Confidence, SHAP Chart Data)
```
