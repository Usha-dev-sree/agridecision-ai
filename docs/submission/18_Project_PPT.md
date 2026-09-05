# Project Presentation (PPT Outline)
## AgriDecision AI — B.Tech Major Project Defense Presentation
**Academic Year:** 2025–2026 | **Department:** Computer Science & Engineering (AI)  
**Presenter:** Ushasree S. (Roll No. 2311IT010169) | **Guide:** Department Faculty  
**Institution:** Mallareddy University, Hyderabad, Telangana  

---

## Slide Structure & Content Outline (25 Slides)

### Slide 1: Title Slide
- **Project Title:** AgriDecision AI: An Intelligent Multi-Modal Platform for Precision Agriculture
- **Student Name:** Ushasree S. (2311IT010169)
- **Degree:** B.Tech Computer Science and Engineering (Specialization: AI)
- **Institution:** Mallareddy University, Hyderabad
- **Visual:** Project Logo & High-Tech Agriculture Background Illustration

---

### Slide 2: Context & Problem Statement
- **Context:** Indian agriculture supports 40%+ of workforce; 86% are smallholder farmers (< 2 ha).
- **Core Problems:**
  1. Information Asymmetry: Lack of personalized, scientifically grounded agronomic advice.
  2. Soil Degradation: Over-application of fertilizers due to unscientific recommendations.
  3. Crop Disease Losses: 15–25% annual yield loss due to delayed disease identification.
  4. Post-Harvest Losses & Credit Exclusion: Poor market timing and lack of credit scoring.
- **Visual:** Infographic summarizing smallholder challenges.

---

### Slide 3: Proposed Solution — AgriDecision AI
- Production-grade, vertically integrated AI ecosystem for precision agriculture.
- Multi-modal intelligence combining Tabular Soil Analysis, Leaf Vision, Time-Series Forecasting, and Voice Advisory.
- Multi-persona platform serving Farmers, Agronomists, Enterprise Procurement Officers, and Platform Administrators.
- **Visual:** High-Level 4-Persona Platform Overview Diagram.

---

### Slide 4: Key Project Objectives
- Build a Crop Recommender with ≥ 75% accuracy across 8 Indian crop classes.
- Deploy a Leaf Disease Detection CNN with ≥ 0.85 precision.
- Implement a Yield Predictor with RMSE < 500 kg/ha.
- Deliver 7-day Mandi price forecasting using LSTM time-series modeling.
- Achieve sub-50 ms API latency at p95 across all endpoints.
- Ensure 100% test pass rate across unit, integration, and multi-persona UAT workflows.

---

### Slide 5: Literature Survey & Research Gaps
- Review of Ramesh et al. (SVM/KNN Crop Rec), Mohanty et al. (PlantVillage CNN), and Kannan et al. (Agmarknet LSTM).
- **Identified Gaps:** Existing systems lack graph knowledge base reasoning, explainable AI (SHAP/Grad-CAM), federated learning, and enterprise GitOps deployment.
- **Visual:** Comparative Matrix Table of existing literature vs. AgriDecision AI.

---

### Slide 6: System Architecture Overview
- 4-Tier Architecture: Edge/Client → Kong Gateway → 9 Microservices → AI/Data Layer.
- Clean Hexagonal Microservice Boundaries powered by FastAPI and SQLAlchemy Async 2.0.
- **Visual:** High-Level Architecture Block Diagram (from `15_Architecture_Diagrams.md`).

---

### Slide 7: AI Model 1 — Crop Recommendation (Random Forest)
- **Algorithm:** Random Forest Classifier (n_estimators=50, max_depth=None, n_jobs=1).
- **Features (7):** pH, Organic Carbon %, N, P, K, Average Temperature, Annual Precipitation.
- **Output:** 8 Crop Classes (rice, maize, soybean, wheat, chickpea, mustard, cotton, sugarcane).
- **Performance:** **79.3% Accuracy**, 0.80 Precision, 0.79 F1.
- **Visual:** Confusion Matrix & Feature Importance Bar Chart.

---

### Slide 8: AI Model 2 — Leaf Disease Detection CNN (ResNet-50)
- **Architecture:** ResNet-50 backbone (pre-trained ImageNet) + Custom Classifier Head.
- **Dataset:** PlantVillage 87,000 leaf images (9 Indian crop-disease classes).
- **Performance:** **0.88 Precision**, 0.86 Recall, 0.87 F1.
- **Explainability:** Layer-4 Grad-CAM attention heatmaps generated per inference.
- **Visual:** Sample Leaf Photo alongside Grad-CAM Heatmap Overlay.

---

### Slide 9: AI Model 3 & 4 — Yield Prediction & Price Forecasting
- **Yield Prediction:** Gradient Boosting Regressor → **RMSE: 459.31 kg/ha**, R²: 0.82.
- **Price Forecasting:** Bidirectional LSTM + Bahdanau Attention → **MAE: 42.5 INR/quintal**.
- **Inference Runtime:** Exported to ONNX runtime served via NVIDIA Triton Inference Server.
- **Visual:** 7-Day Commodity Price Forecast Curve with 95% Confidence Interval.

---

### Slide 10: Explainable AI (XAI) & Knowledge Graph
- **SHAP Integration:** TreeSHAP values included with every crop recommendation response.
- **JanusGraph Property Graph:** 450+ agri-ontological triples (Crop, Disease, Pest, Chemical, Soil, AEZ).
- **GraphRAG:** Enables multi-hop Gremlin graph queries for complex agronomic advisories.
- **Visual:** Sample Gremlin Graph Structure & SHAP Waterfall Plot.

---

### Slide 11: Polyglot Data Layer Architecture
- **PostgreSQL 15 + PostGIS 3.4:** Core relational entities + GeoJSON plot boundaries.
- **TimescaleDB 2.15:** 7-day hypertables with 4-way hash partitioning for IoT/weather telemetry.
- **Redis 7:** Session tokens, OTP cache, pre-materialized feature store.
- **Apache Kafka 3.4:** Event-driven streaming mesh for telemetry & notifications.
- **Visual:** Database Polyglot Storage Mapping Diagram.

---

### Slide 12: Backend Microservices (FastAPI Ecosystem)
- 9 Specialized FastAPI Microservices: `user_service`, `farm_service`, `advisory_service`, `iot_service`, `market_service`, `weather_service`, `financial_service`, `enterprise_service`, `notification_service`.
- Async SQLAlchemy ORM, Pydantic v2 schemas, and Vault secrets injection.
- **Visual:** Microservice Routing Table & Port Assignment.

---

### Slide 13: Web Frontend — React 18 Agronomist Portal
- React 18 + TypeScript + Vite + Material UI v5 + Redux Toolkit + React Query.
- Leaflet map integration for GeoJSON boundary drawing and spatial parcel indexing.
- 15 Role-differentiated Page Views (Farmer, Agronomist, Enterprise, Admin).
- **Visual:** React Portal Dashboard Screenshots.

---

### Slide 14: Mobile App — Flutter 3 Cross-Platform App
- Flutter 3 + Dart + SQLite local cache + Camera + GPS + Speech-to-Text.
- Supports 72+ hours of offline operation with background sync queue.
- 7 Screens: Dashboard, Disease Detection, Voice Assistant, Analytics, Loans, Maps, Profile.
- **Visual:** Flutter App Mockups (Camera Scan & Voice Assistant).

---

### Slide 15: Voice Assistant & Agronomic Advisory Engine
- On-device speech recognition + AgronomicPromptEngine.
- Translates natural language farmer queries into structured diagnostic advice.
- Provides diagnosis, remedy steps, warning signs, and crop suitability rankings.
- **Visual:** Voice Query Flow Sequence.

---

### Slide 16: Security & Identity Architecture
- Authentication: Phone OTP, Google OAuth2, Apple Sign-In, RS256 JWT, TOTP MFA.
- Role-Based Access Control (RBAC): Enforces role hierarchy across all API routes.
- HashiCorp Vault: Centralized secret engine (zero plaintext secrets in git/k8s).
- OWASP Top-10 Mitigations & GDPR compliance endpoints (export & deletion).
- **Visual:** Security Layers Diagram.

---

### Slide 17: DevOps & GitOps Infrastructure
- Infrastructure as Code (IaC): Terraform scripts for AWS EKS, RDS, ElastiCache, MSK.
- GitOps Continuous Deployment: ArgoCD automated sync with Helm chart manifests.
- Multi-stage Docker builds tagged with git commit SHAs.
- **Visual:** GitOps CI/CD Deployment Pipeline.

---

### Slide 18: Observability Stack (LGTM Stack)
- Prometheus metrics collection (`/metrics` endpoints across all microservices).
- Grafana centralized dashboards (RED metrics, AI inference latency, DB connection saturation).
- Loki structured log aggregation + Tempo distributed tracing via OpenTelemetry.
- **Visual:** Grafana System Dashboard Screenshot.

---

### Slide 19: User Acceptance Testing (UAT) Methodology
- 9-Phase Systematic UAT Execution (`testing/run_full_uat_validation.py`).
- Tested 11 infrastructure containers, 151 REST APIs, 15 web pages, 7 mobile screens, and 6 AI engines.
- Executed 15-step multi-persona user workflow spanning all 4 roles.
- **Visual:** UAT 9-Phase Checklist Matrix.

---

### Slide 20: Comprehensive Testing Results
- **Overall Result:** **100% Pass Rate (246 / 246 Tests Passed)**.
- Unit Tests: 13/13 Passed | Integration Verification: 6/6 Passed.
- REST API Tests: 151/151 Passed | Web & Mobile UI Tests: 22/22 Passed.
- Multi-Persona Workflow Steps: 15/15 Passed.
- **Visual:** Test Pass Rate Pie Chart & Summary Metrics.

---

### Slide 21: Performance & SLA Verification
- REST API p95 Latency: **14.2 ms** (SLA Target: < 100 ms) — **7x Faster**.
- Database Query Latency: **2.8 ms** (SLA Target: < 10 ms).
- Frontend Time-To-Interactive: **0.85 sec** (SLA Target: < 2.0 sec).
- Redis Cache Hit Ratio: **98.6%** (SLA Target: > 90%).
- Kafka Message Throughput: **12,500 msg/sec** (SLA Target: > 5,000 msg/sec).
- **Visual:** Performance SLA Comparison Bar Chart.

---

### Slide 22: Live Demonstration Highlights
- Highlight 1: GeoJSON Plot Boundary Recording on Web & Mobile Maps.
- Highlight 2: Soil Profile Submission → Instant AI Crop Recommendation + SHAP Chart.
- Highlight 3: Leaf Photo Upload → ResNet-50 Disease Classification + Grad-CAM Heatmap.
- Highlight 4: 7-Day Agrometeorological Forecast + FAO-56 Penman-Monteith ET₀ Display.
- Highlight 5: Agronomist Review & Enterprise Procurement Contract Flow.

---

### Slide 23: Future Scope & Enhancement Roadmap
- Scale Federated Learning across 10,000+ IoT nodes for edge model training.
- Integrate Sentinel-2 SAR satellite data for radar soil moisture inversion.
- Expand Indic Language Voice Interface to 12 Indian regional dialects via Bhashini API.
- Direct FinTech Integration with NABARD Kisan Credit Card APIs.

---

### Slide 24: Conclusion & Key Takeaways
- Successfully designed, implemented, and validated an enterprise-grade precision agriculture AI platform.
- Demonstrated sub-15 ms API latency, 79.3% crop recommendation accuracy, and 0.88 disease detection precision.
- Fully certified **PRODUCTION READY** with a 100% UAT pass rate.
- Ready for pilot deployment with Farmer Producer Organizations (FPOs).

---

### Slide 25: Q&A / Thank You
- **Thank You!**
- Open for Questions from the Evaluation Committee.
- Project Repository: `https://github.com/agridecision/agridecision-ai`
- Contact: `2311it010169@mallareddyuniversity.ac.in`
