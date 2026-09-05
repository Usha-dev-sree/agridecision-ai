# 🌾 AgriDecision AI — Production Agricultural Intelligence System

[![CI/CD Pipeline](https://github.com/agridecision/agridecision-ai/actions/workflows/agri-devops.yml/badge.svg)](https://github.com/agridecision/agridecision-ai/actions/workflows/agri-devops.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.2.0-61dafb.svg)](https://react.dev/)
[![Flutter 3.x](https://img.shields.io/badge/Flutter-3.x-02569B.svg)](https://flutter.dev/)
[![UAT Status](https://img.shields.io/badge/UAT_Pass_Rate-100%25-success.svg)](docs/submission/12_Testing_Report.md)

AgriDecision AI is an enterprise-grade, production-grade artificial intelligence ecosystem designed for modern precision agriculture, yield prediction, multi-spectral soil analysis, real-time agrometeorological forecasting, leaf disease diagnosis, and agricultural credit scoring.

---

## 🏛 Architecture Overview

AgriDecision AI is structured as a monorepo consisting of:

- **AI Inference Engine** (`ai_services/`): Triton Inference Server configuration, ResNet-50 CNN leaf disease classifier, Random Forest crop recommendation classifier, Gradient Boosting yield regressor, BiLSTM market price forecaster, and LLM voice advisory engine.
- **Backend Microservices** (`backend/services/`): 9 domain-bounded FastAPI services: IAM (`user_service`), Farm/Soil (`farm_service`), Agronomic Recommendations (`advisory_service`), IoT (`iot_service`), Mandi Rates (`market_service`), Weather (`weather_service`), Credit (`financial_service`), Contracts (`enterprise_service`), and Notifications (`notification_service`).
- **Web Frontend** (`frontend/apps/agronomist-portal`): Production React 18 SPA built with TypeScript, Vite, Material UI v5, Redux Toolkit, React Query v5, and Leaflet map polygon boundary editor.
- **Mobile Application** (`mobile/`): Production Flutter 3 app supporting offline SQLite caching, camera leaf snapshot diagnosis, GPS plot boundary scanner, and voice assistant.
- **Datastores & Infra** (`database/`, `devops/`, `infrastructure/`): PostgreSQL + PostGIS, TimescaleDB hypertables, Redis 7 cache, Apache Kafka 3.4, HashiCorp Vault 1.13, Kong API Gateway 3.2, AWS EKS (Terraform), Helm charts, and LGTM observability stack (Loki, Grafana, Tempo, Prometheus).

---

## 🚀 Quick Start

### Local Infrastructure Setup (Docker Compose)
Spins up all datastores, microservices, Kong Gateway, and observability tools:

```bash
# 1. Clone repository
git clone https://github.com/agridecision/agridecision-ai.git
cd agridecision-ai

# 2. Launch complete infrastructure stack
docker-compose up -d

# 3. Initialize Vault secrets
bash devops/vault/vault-init.sh
```

### Launch React Agronomist Portal
```bash
cd frontend/apps/agronomist-portal
npm install
npm run dev
# Portal accessible at http://localhost:3000
```

### Launch Flutter Mobile Application
```bash
cd mobile
flutter pub get
flutter run
```

---

## 🧪 Testing & Verification

Run the automated test suite across all verification layers:

```bash
# 1. Run backend unit tests
python -m unittest testing/unit/test_services.py

# 2. Run end-to-end AI system verification
python testing/run_ai_system_verification.py

# 3. Run full 9-phase UAT validation
python testing/run_full_uat_validation.py
```

---

## 📁 Final Submission Package

Complete B.Tech Major Project documentation is available in [`docs/submission/`](docs/submission/):

1. [`01_IEEE_Research_Paper.md`](docs/submission/01_IEEE_Research_Paper.md) — Camera-ready IEEE format manuscript.
2. [`02_Final_Project_Report.md`](docs/submission/02_Final_Project_Report.md) — Comprehensive project report.
3. [`03_Software_Requirements_Specification.md`](docs/submission/03_Software_Requirements_Specification.md) — IEEE std 830 compliant SRS.
4. [`04_Software_Design_Document.md`](docs/submission/04_Software_Design_Document.md) — Detailed SDD.
5. [`05_API_Documentation.md`](docs/submission/05_API_Documentation.md) — OpenAPI v3 REST API reference.
6. [`06_Database_Documentation.md`](docs/submission/06_Database_Documentation.md) — Relational, Time-Series & Graph DB reference.
7. [`07_AI_Model_Documentation.md`](docs/submission/07_AI_Model_Documentation.md) — Model cards, ONNX & Triton reference.
8. [`08_Deployment_Guide.md`](docs/submission/08_Deployment_Guide.md) — Docker Compose, Kubernetes & GitOps guide.
9. [`09_User_Manual.md`](docs/submission/09_User_Manual.md) — Farmer, Agronomist & Enterprise guide.
10. [`10_Administrator_Manual.md`](docs/submission/10_Administrator_Manual.md) — Admin governance & LGTM stack guide.
11. [`11_Installation_Guide.md`](docs/submission/11_Installation_Guide.md) — Step-by-step setup guide.
12. [`12_Testing_Report.md`](docs/submission/12_Testing_Report.md) — Complete test execution report.
13. [`13_Security_Report.md`](docs/submission/13_Security_Report.md) — OWASP Top-10 & Vault audit report.
14. [`14_Performance_Report.md`](docs/submission/14_Performance_Report.md) — Performance SLA benchmark report.
15. [`15_Architecture_Diagrams.md`](docs/submission/15_Architecture_Diagrams.md) — System architecture diagrams.
16. [`16_ER_Diagram.md`](docs/submission/16_ER_Diagram.md) — Relational ER & Property Graph diagrams.
17. [`17_UML_Diagrams.md`](docs/submission/17_UML_Diagrams.md) — Use Case, Class, Activity, Sequence, Deployment diagrams.
18. [`18_Project_PPT.md`](docs/submission/18_Project_PPT.md) — 25-slide defense presentation outline.
19. [`19_Viva_Questions_with_Answers.md`](docs/submission/19_Viva_Questions_with_Answers.md) — Viva Voce study guide.
20. [`20_README.md`](docs/submission/20_README.md) — Master submission index.
21. [`21_LICENSE.md`](docs/submission/21_LICENSE.md) — MIT Open Source License.
22. [`22_Contributing_Guide.md`](docs/submission/22_Contributing_Guide.md) — Developer guidelines.
23. [`23_Final_Project_Completion_Certificate.md`](docs/submission/23_Final_Project_Completion_Certificate.md) — Certified Completion Certificate.

---

## 📄 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
