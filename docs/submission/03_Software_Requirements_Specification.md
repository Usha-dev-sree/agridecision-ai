# Software Requirements Specification (SRS)
## AgriDecision AI — Intelligent Precision Agriculture Platform
**Document Version:** 1.0 | **Date:** July 28, 2026 | **Status:** Final

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the functional, non-functional, interface, and constraint requirements for AgriDecision AI — a production-grade intelligent decision support platform for Indian precision agriculture.

### 1.2 Intended Audience
- B.Tech Evaluation Committee — Mallareddy University
- Software Development Team
- QA & Testing Team
- Deployment & DevOps Engineers
- Future Maintainers

### 1.3 Definitions

| Term | Definition |
| :--- | :--- |
| Farmer | Primary end-user who registers farm plots and receives agronomic guidance |
| Agronomist | Certified professional who reviews AI recommendations and provides expert annotations |
| Enterprise User | Procurement officer managing supply-side agricultural contracts |
| Admin | Platform administrator managing users, system telemetry, and audit logs |
| Farm Plot | A geographically bounded agricultural parcel with associated soil and crop data |
| Soil Profile | Tabular record of soil chemical properties (pH, N, P, K, OC%, EC) |
| ONNX Model | Open Neural Network Exchange format model deployed on Triton Inference Server |
| Hypertable | TimescaleDB time-partitioned table for IoT/weather time-series data |
| JWT | JSON Web Token — RS256-signed authentication credential |

---

## 2. Overall Description

### 2.1 Product Perspective
AgriDecision AI is a greenfield, full-stack platform comprising:
- A **FastAPI monorepo** with 10 microservices
- A **React 18 TypeScript** web portal (Agronomist + Farmer + Enterprise + Admin views)
- A **Flutter 3 Dart** mobile application
- An **AI inference gateway** powered by NVIDIA Triton Inference Server + ONNX Runtime
- A **JanusGraph knowledge graph** with 450+ agri-ontological triples
- A **polyglot data layer** (PostgreSQL, TimescaleDB, Redis, JanusGraph)
- An **event-streaming mesh** (Apache Kafka + ZooKeeper)
- An **LGTM observability stack** (Prometheus, Grafana, Loki, Tempo)

### 2.2 Operating Environment
- **Backend:** Linux containers (Alpine-based), Python 3.11
- **Frontend:** Modern browsers (Chrome 120+, Firefox 120+, Safari 16+)
- **Mobile:** Android 8.0+, iOS 15+
- **Infrastructure:** Kubernetes 1.29+ (AWS EKS for production, Docker Compose for local)
- **CI/CD:** GitHub Actions → Harbor Registry → ArgoCD

---

## 3. Functional Requirements

### 3.1 User Management (user_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-001 | System shall send OTP to registered phone within 5 seconds | HIGH |
| FR-002 | System shall verify OTP and issue JWT access + refresh tokens | HIGH |
| FR-003 | System shall support Google OAuth2 ID token login | HIGH |
| FR-004 | System shall support Apple Sign-In JWT validation | MEDIUM |
| FR-005 | System shall support TOTP-based MFA with QR code provisioning | HIGH |
| FR-006 | System shall provision user accounts with role assignment (FARMER, AGRONOMIST, ENTERPRISE, ADMIN) | HIGH |
| FR-007 | System shall support GDPR data export as JSON archive within 30 days of request | HIGH |
| FR-008 | System shall perform GDPR data deletion (anonymization) within 30 days of request | HIGH |
| FR-009 | System shall store session tokens in Redis with JTI blacklist on logout | HIGH |
| FR-010 | System shall maintain audit logs for all authentication events | MEDIUM |

### 3.2 Farm Management (farm_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-011 | System shall allow creation of farm plots with name, area (ha), and irrigation type | HIGH |
| FR-012 | System shall store farm plot boundaries as GeoJSON polygons in PostGIS | HIGH |
| FR-013 | System shall compute and store plot centroid coordinates | MEDIUM |
| FR-014 | System shall allow upload of soil profiles (pH, N, P, K, OC%, EC, texture) | HIGH |
| FR-015 | System shall validate soil profile values against agronomic physical bounds | HIGH |
| FR-016 | System shall support crop season records with sowing and harvest dates | MEDIUM |
| FR-017 | System shall support IoT device registration and association with farm plots | MEDIUM |
| FR-018 | System shall provide spatial query for farms within a defined radius | MEDIUM |

### 3.3 AI Advisory (advisory_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-019 | System shall return crop recommendation (8 classes) within 200ms of soil profile submission | HIGH |
| FR-020 | System shall provide SHAP feature attribution values with every recommendation | HIGH |
| FR-021 | System shall accept JPEG/PNG leaf images (max 5MB) for disease detection | HIGH |
| FR-022 | System shall return disease classification result within 500ms of image upload | HIGH |
| FR-023 | System shall generate Grad-CAM attention heatmap for every disease detection | HIGH |
| FR-024 | System shall log all AI recommendations with model version to database | HIGH |
| FR-025 | System shall support natural language agronomic advisory queries | MEDIUM |
| FR-026 | System shall return advisory with diagnosis, remedy_steps, warning_signs, and crop_suitability | MEDIUM |

### 3.4 IoT Telemetry (iot_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-027 | System shall accept sensor telemetry (temp, humidity, soil moisture, conductivity) | HIGH |
| FR-028 | System shall store telemetry in TimescaleDB with 7-day chunk partitioning | HIGH |
| FR-029 | System shall compute soil moisture deficit from telemetry + ET₀ | MEDIUM |
| FR-030 | System shall bridge MQTT → Kafka for IoT node integration | HIGH |

### 3.5 Market Intelligence (market_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-031 | System shall display real-time Mandi commodity prices | HIGH |
| FR-032 | System shall display 7-day commodity price forecasts from LSTM model | HIGH |
| FR-033 | System shall support price history queries by commodity, date range, and mandi | MEDIUM |

### 3.6 Weather Intelligence (weather_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-034 | System shall display 7-day agrometeorological forecast for a given farm plot | HIGH |
| FR-035 | System shall compute ET₀ using FAO-56 Penman-Monteith method | HIGH |
| FR-036 | System shall store historical weather observations in TimescaleDB | HIGH |

### 3.7 Financial Services (financial_service)

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-037 | System shall compute agricultural credit risk score from land area, income, and debt obligations | HIGH |
| FR-038 | System shall allow submission of loan applications with purpose, amount, and collateral | HIGH |
| FR-039 | System shall display government scheme eligibility based on farmer profile | MEDIUM |

### 3.8 Enterprise & Notifications

| ID | Requirement | Priority |
| :--- | :--- | :---: |
| FR-040 | Enterprise users shall create procurement contracts linked to farm plots | HIGH |
| FR-041 | System shall dispatch SMS notifications via Twilio on key agronomic events | HIGH |
| FR-042 | System shall dispatch FCM push notifications to mobile devices | HIGH |
| FR-043 | System shall dispatch email notifications via SendGrid | MEDIUM |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement |
| :--- | :--- |
| NFR-001 | REST API p95 latency shall not exceed 100ms under 1,000 concurrent users |
| NFR-002 | AI tabular inference response shall not exceed 200ms |
| NFR-003 | AI image inference response shall not exceed 500ms |
| NFR-004 | Frontend Time-to-Interactive shall not exceed 2.0 seconds |
| NFR-005 | Kafka message throughput shall sustain ≥ 5,000 messages/second |

### 4.2 Security

| ID | Requirement |
| :--- | :--- |
| NFR-006 | All API routes shall validate JWT RS256 tokens |
| NFR-007 | RBAC shall enforce role-level access controls on all protected routes |
| NFR-008 | TLS 1.3 minimum shall be enforced at Kong gateway |
| NFR-009 | All secrets shall be managed via HashiCorp Vault KV-v2 engine |
| NFR-010 | PII columns shall be encrypted at rest using AES-256 via pgcrypto |
| NFR-011 | Rate limiting shall be enforced at 100 requests/minute per client IP |
| NFR-012 | OWASP security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options) shall be injected by Kong |

### 4.3 Reliability & Availability

| ID | Requirement |
| :--- | :--- |
| NFR-013 | Platform uptime shall be ≥ 99.5% (2.19 hours/year planned downtime) |
| NFR-014 | Each microservice shall have at minimum 2 replica Kubernetes pods |
| NFR-015 | PodDisruptionBudgets shall prevent all replicas from being unavailable simultaneously |
| NFR-016 | Database connections shall use connection pooling (SQLAlchemy AsyncSession with max_overflow=20) |

### 4.4 Scalability

| ID | Requirement |
| :--- | :--- |
| NFR-017 | HPA shall scale pods from 2 to 10 replicas based on CPU utilization threshold of 70% |
| NFR-018 | TimescaleDB chunk policy shall auto-compress chunks older than 30 days |
| NFR-019 | Redis cluster shall be deployed in cluster mode supporting horizontal sharding |

### 4.5 Maintainability & Observability

| ID | Requirement |
| :--- | :--- |
| NFR-020 | All microservices shall expose OpenTelemetry traces exported to Grafana Tempo |
| NFR-021 | All microservices shall expose Prometheus `/metrics` endpoints |
| NFR-022 | All logs shall be structured JSON forwarded to Grafana Loki |
| NFR-023 | Grafana dashboards shall display service RED metrics (Rate, Errors, Duration) |

---

## 5. Interface Requirements

### 5.1 User Interfaces

- **Web Portal:** React 18 SPA, responsive at 375px (Mobile), 768px (Tablet), 1440px (Desktop), Material UI v5 component library, WCAG 2.1 AA compliant
- **Mobile App:** Flutter 3 native iOS/Android, offline-capable via SQLite, camera and GPS hardware access

### 5.2 Hardware Interfaces

- **IoT Sensors:** MQTT-compatible soil and weather sensors (temperature, humidity, soil moisture, pH probes) communicating via MQTT 3.1.1 over TCP/IP
- **Mobile Camera:** iOS/Android native camera access via Flutter `image_picker` plugin for leaf disease photo capture

### 5.3 Software Interfaces

- **Kong API Gateway:** All external API traffic routed through Kong 3.2 with JWT plugin, rate-limiting plugin, CORS plugin, and response-transformer plugin
- **HashiCorp Vault:** Application pods authenticate via Kubernetes ServiceAccount tokens; secrets injected via Vault Agent Sidecar
- **Triton Inference Server:** advisory_service communicates with Triton via HTTP REST API (`/v2/models/{model}/infer`) using KServe V2 inference protocol

### 5.4 Communication Interfaces

- **External:** HTTPS (TLS 1.3) for all client-server communication
- **Internal:** HTTP/1.1 REST for synchronous inter-service calls; Kafka PLAINTEXT for internal async messaging
- **IoT:** MQTT 3.1.1 over TCP port 1883, bridged to Kafka by iot_service

---

## 6. Constraints

- Platform must function without NVIDIA GPU on development environments (ONNX CPU Runtime fallback)
- PyTorch c10.dll initialization may fail on non-AVX2-capable hosts; fallback metrics and ONNX stubs substitute
- Vault must be initialized and unsealed before backend services start
- Kafka requires ZooKeeper to be healthy before broker registration
- TimescaleDB extension must be available on PostgreSQL instance (requires TimescaleDB-HA image)
- Flutter mobile app requires Google Services JSON (Android) and APNs certificate (iOS) for push notifications
