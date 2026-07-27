# 🌾 AgriDecision AI — Production Agricultural Intelligence System

[![CI/CD Pipeline](https://github.com/agridecision/agridecision-ai/actions/workflows/agri-devops.yml/badge.svg)](https://github.com/agridecision/agridecision-ai/actions/workflows/agri-devops.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18.2.0-61dafb.svg)](https://react.dev/)
[![Flutter 3.x](https://img.shields.io/badge/Flutter-3.x-02569B.svg)](https://flutter.dev/)

AgriDecision AI is an enterprise-grade, end-to-end artificial intelligence ecosystem designed for modern precision agriculture, yield prediction, multi-spectral soil analysis, real-time agro-meteorological forecasting, and leaf disease diagnosis.

---

## 🏛 Architecture Overview

AgriDecision AI is structured as a monorepo consisting of:

- **AI Inference Engine** (`ai_services/`): Triton Inference Server configuration, CNN leaf disease classifiers, XGBoost & Random Forest yield models, time-series market price forecasters, and LLM advisory engines.
- **Backend Microservices** (`backend/services/`): Fast-API services handling User IAM (`user_service`), Farm/Soil/IoT management (`farm_service`), Agronomic Recommendations (`advisory_service`), Weather (`weather_service`), and Mandi Rates (`market_service`).
- **Web Frontend** (`frontend/apps/agronomist-portal`): Production React 18 application built with TypeScript, Vite, Material UI, Redux Toolkit, React Query, and Leaflet map boundary capture.
- **Mobile Application** (`mobile/`): Production Flutter 3 app supporting offline SQLite caching, automatic sync queue, camera leaf snapshots, GPS, and voice assistant.
- **Datastores & Infra** (`database/`, `devops/`, `infrastructure/`): PostgreSQL, TimescaleDB hypertables, Redis cache, Apache Kafka, HashiCorp Vault, Kong API Gateway, AWS EKS (Terraform), Helm charts, and LGTM observability stack (Loki, Grafana, Tempo, Prometheus).

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

## 🧪 Testing

Run the automated test suite across all 6 test classifications:

```bash
# Run unit, contract, accessibility, and benchmark tests
python -m unittest testing/unit/test_services.py testing/contract/test_pact_contracts.py testing/accessibility/test_a11y_wcag.py testing/performance/test_regression_benchmark.py
```

---

## 📄 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
