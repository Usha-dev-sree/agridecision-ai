# Viva Questions with Answers
## AgriDecision AI — Comprehensive B.Tech Viva Voce Guide
**Academic Year:** 2025–2026 | **Specialization:** Artificial Intelligence  
**Institution:** Mallareddy University, Hyderabad  

---

## Section 1: System Architecture & Design

### Q1: Explain the overall architecture of AgriDecision AI.
**Answer:** AgriDecision AI follows a domain-driven, 4-tier microservices architecture:
1. **Edge/Client Layer:** Flutter 3 mobile client (offline SQLite, GPS, camera) and React 18 web portal.
2. **Gateway & Security Layer:** Kong API Gateway (TLS 1.3, RS256 JWT validation, rate limiting) backed by HashiCorp Vault for secrets management.
3. **Backend Microservices Layer:** 9 domain-bounded FastAPI services (`user_service`, `farm_service`, `advisory_service`, `iot_service`, `market_service`, `weather_service`, `financial_service`, `enterprise_service`, `notification_service`).
4. **AI & Polyglot Data Layer:** NVIDIA Triton Inference Server running ONNX models, JanusGraph property graph, PostgreSQL + PostGIS, TimescaleDB hypertables, Redis cache/feature store, and Apache Kafka event mesh.

---

### Q2: Why did you choose FastAPI over Flask or Django for the microservices?
**Answer:** FastAPI was selected for three primary technical advantages:
1. **Asynchronous Performance:** Built on Starlette and Uvicorn, supporting native Python `async/await` concurrency for non-blocking I/O (essential for high-concurrency DB and API operations).
2. **Automatic OpenAPI / Swagger Documentation:** Built-in Pydantic schema validation auto-generates interactive API docs.
3. **High Throughput:** Benchmark studies show FastAPI achieves speeds comparable to NodeJS and Go, handling 10,000+ req/sec efficiently.

---

### Q3: What is the role of Kong API Gateway in your architecture?
**Answer:** Kong serves as the single ingress entrypoint for all incoming client traffic. It performs:
- **TLS Termination:** Encrypts external HTTPS traffic.
- **JWT Verification:** Validates RS256-signed JWT access tokens before forwarding requests to backend microservices.
- **Rate Limiting:** Protects backend services against DDoS attacks (configured at 100 req/min per IP).
- **CORS Enforcement & OWASP Header Injection:** Adds security headers (HSTS, CSP, X-Frame-Options).

---

## Section 2: Artificial Intelligence & Machine Learning

### Q4: Which machine learning models are deployed in AgriDecision AI?
**Answer:** We deployed four specialized models:
1. **Crop Recommendation Model (CRM):** Random Forest Classifier (79.3% accuracy, 8 output crop classes based on soil NPK, pH, OC%, temp, rain).
2. **Yield Prediction Model (YPM):** Gradient Boosting Regressor (RMSE: 459.31 kg/ha, R²: 0.82).
3. **Leaf Disease Detection CNN (DDM):** ResNet-50 Convolutional Neural Network (0.88 precision across 9 Indian crop-disease classes).
4. **Commodity Price Forecasting Model (PFM):** Bidirectional LSTM with Bahdanau Attention (MAE: 42.5 INR/quintal, 7-day forward window).

---

### Q5: How do you achieve Explainable AI (XAI) in your models?
**Answer:**
- **Tabular Models (Crop & Yield):** We integrate **SHAP (SHapley Additive exPlanations)** using `shap.TreeExplainer`. This quantifies the exact contribution of each soil feature (e.g., pH +0.18, Nitrogen +0.22) to the final prediction.
- **Vision Models (Leaf Disease CNN):** We compute **Grad-CAM (Gradient-weighted Class Activation Mapping)** heatmaps from the final residual block (`layer4`) of ResNet-50. This generates a visual attention overlay showing farmers the exact spot on the leaf where disease symptoms were detected.

---

### Q6: Why did you export models to ONNX format and use Triton Inference Server?
**Answer:**
- **ONNX (Open Neural Network Exchange):** Provides a framework-agnostic runtime format, allowing models trained in Scikit-Learn or PyTorch to run on a uniform, highly optimized C++ runtime engine without needing heavy Python dependencies.
- **Triton Inference Server:** Provides production-grade model serving features including dynamic batching, concurrent model execution across CPU/GPU instances, model versioning, and zero-downtime model updates via KServe V2 REST/gRPC protocols.

---

### Q7: What happens if Triton Inference Server goes down?
**Answer:** We implemented **Rule-Based Fallback Engines** in `ai_services/inference_gateway/fallback_rules.py`. If Triton is unreachable, the system automatically routes requests through deterministic agronomic rule sets (e.g., pH/rainfall thresholds from ICAR guidelines). The response includes `"fallback_used": true` so users and agronomists know a fallback rule was applied.

---

## Section 3: Databases & Data Engineering

### Q8: Explain your polyglot database strategy.
**Answer:** Different data workloads require specialized data engines:
- **PostgreSQL + PostGIS:** Handles relational transactional data (users, farms, loans) and spatial boundary polygons using GIS indexes (`GIST`).
- **TimescaleDB:** Handles high-volume time-series telemetry (IoT sensors, weather observations, market prices) using 7-day hypertable chunks and 4-way hash partitioning.
- **Redis:** Serves as an in-memory session store, OTP token cache, rate-limit tracker, and pre-materialized feature store for sub-10 ms AI inference.
- **JanusGraph:** Property graph database storing 450+ agri-ontological relationship triples for multi-hop GraphRAG reasoning.

---

### Q9: What is a TimescaleDB Hypertable, and why did you use it?
**Answer:** A hypertable is an abstraction layer in TimescaleDB that automatically partitions time-series tables into smaller, time-bounded physical tables called "chunks" (configured to 7-day intervals). This maintains fast index lookup performance even as the database grows to millions of rows, avoiding the performance degradation seen in standard relational tables.

---

## Section 4: Security & DevOps

### Q10: How do you handle secrets management in AgriDecision AI?
**Answer:** We enforce a strict **zero-plaintext-credential policy**. All database connection URLs, RSA keys, and API keys are stored in HashiCorp Vault's KV-v2 secret engine under `kv/data/agri/*`. Production Kubernetes pods use the Vault Agent Sidecar Injector to mount secrets directly into pod memory at startup.

---

### Q11: Explain your GitOps deployment pipeline.
**Answer:**
1. Code changes pushed to GitHub trigger `.github/workflows/agri-devops.yml`.
2. Pipeline runs linters, unit tests, and security scans.
3. Successful builds generate Docker images tagged with git commit SHAs and push them to Harbor registry.
4. **ArgoCD** monitors the Git repository's Helm chart manifests (`infrastructure/helm/agridecision-ai/`) and automatically synchronizes state with the Kubernetes cluster (`agridecision-prod`), providing automated self-healing and zero-downtime rolling updates.

---

## Section 5: Testing & Validation Results

### Q12: What were the results of your User Acceptance Testing (UAT)?
**Answer:** We conducted a comprehensive 9-phase UAT covering 11 infrastructure containers, 151 REST APIs, 15 web pages, 7 mobile screens, 6 AI engines, and a 15-step end-to-end multi-persona workflow. The entire test suite achieved a **100% Pass Rate (246 / 246 tests passed)**.

---

### Q13: What are the key performance metrics achieved by your system?
**Answer:**
- **API Response Latency (p95):** 14.2 ms (SLA Target: < 100 ms) — **7x faster than requirement**.
- **Database Query Latency:** 2.8 ms (SLA Target: < 10 ms).
- **Frontend Time-To-Interactive:** 0.85 sec (SLA Target: < 2.0 sec).
- **Redis Cache Hit Ratio:** 98.6%.
- **Kafka Throughput:** 12,500 messages/sec.
