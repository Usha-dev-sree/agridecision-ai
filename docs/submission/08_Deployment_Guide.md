# Deployment Guide
## AgriDecision AI — Production Deployment Reference
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Prerequisites

### 1.1 Local Development Requirements

| Software | Minimum Version | Purpose |
| :--- | :--- | :--- |
| Docker Desktop | 24.x | Container runtime |
| Docker Compose | v2.x | Local orchestration |
| Python | 3.11+ | Backend development |
| Node.js | 18.x (LTS) | Frontend development |
| Flutter SDK | 3.x | Mobile development |
| Git | 2.x | Version control |

### 1.2 Production Requirements

| Software | Version | Purpose |
| :--- | :--- | :--- |
| kubectl | 1.29+ | Kubernetes CLI |
| Helm | 3.14+ | Kubernetes package manager |
| ArgoCD CLI | 2.9+ | GitOps deployment |
| Terraform | 1.7+ | AWS infrastructure provisioning |
| AWS CLI | 2.x | AWS resource management |

---

## 2. Local Development Deployment (Docker Compose)

### 2.1 Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/agridecision/agridecision-ai.git
cd agridecision-ai

# 2. Copy environment template
cp .env.example .env
# Edit .env with your local settings

# 3. Launch complete infrastructure stack
docker-compose up -d

# 4. Verify all containers are healthy
docker-compose ps
```

### 2.2 Expected Container Status

```
NAME                    STATUS          PORTS
agri-postgres           running         0.0.0.0:5432->5432/tcp
agri-timescaledb        running         0.0.0.0:5433->5432/tcp
agri-redis              running         0.0.0.0:6379->6379/tcp
agri-zookeeper          running         0.0.0.0:2181->2181/tcp
agri-kafka              running         0.0.0.0:9092->9092/tcp
agri-kong               running         0.0.0.0:8000->8000/tcp, 0.0.0.0:8001->8001/tcp
agri-prometheus         running         0.0.0.0:9090->9090/tcp
agri-grafana            running         0.0.0.0:3000->3000/tcp
agri-loki               running         0.0.0.0:3100->3100/tcp
agri-tempo              running         0.0.0.0:3200->3200/tcp
agri-vault              running         0.0.0.0:8200->8200/tcp
```

### 2.3 Database Initialization

```bash
# Initialize PostgreSQL schema (run master migration)
docker exec agri-postgres psql -U agri_user -d agri_db -f /docker-entrypoint-initdb.d/001_master_schema.sql

# Initialize TimescaleDB hypertables
docker exec agri-timescaledb psql -U agri_user -d agri_timeseries -f /docker-entrypoint-initdb.d/002_timescaledb_hypertables.sql
```

### 2.4 Vault Initialization

```bash
# Initialize and unseal Vault (local dev mode uses auto-unseal)
bash devops/vault/vault-init.sh

# Verify Vault status
curl http://localhost:8200/v1/sys/health
# Expected: {"initialized":true,"sealed":false,...}
```

### 2.5 AI Model Training (First Time)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Train all 4 AI models and register in ModelRegistry
python ai_services/training_pipelines/trainers/crop_recommendation.py
python ai_services/training_pipelines/trainers/yield_prediction.py
python ai_services/training_pipelines/trainers/disease_detection.py  # May take 10-20 min
python ai_services/training_pipelines/trainers/price_forecasting.py

# Verify models are in registry
python -c "
from ai_services.model_registry.registry import ModelRegistryManager
mgr = ModelRegistryManager()
models = mgr.list_all_versions()
for m in models:
    print(m['name'], m['version'], m['status'])
"
```

### 2.6 Backend Service Launch

```bash
# Start all FastAPI microservices (development mode with hot-reload)
# user_service
cd backend/services/user_service
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload &

# farm_service
cd backend/services/farm_service
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload &

# advisory_service
cd backend/services/advisory_service
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload &

# Repeat for remaining services (8004-8009)
```

### 2.7 Frontend Launch

```bash
# React Agronomist Portal
cd frontend/apps/agronomist-portal
npm install
npm run dev
# Portal accessible at http://localhost:3000

# Flutter Mobile App (requires Android emulator or iOS simulator)
cd mobile
flutter pub get
flutter run
```

---

## 3. Production Kubernetes Deployment (AWS EKS)

### 3.1 Infrastructure Provisioning (Terraform)

```bash
# Navigate to Terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review execution plan
terraform plan -var-file="production.tfvars"

# Apply infrastructure (creates EKS cluster, RDS, ElastiCache, MSK)
terraform apply -var-file="production.tfvars" -auto-approve

# Configure kubectl
aws eks update-kubeconfig --region ap-south-1 --name agridecision-prod
```

**Resources Created:**
- EKS Cluster (v1.29): 3-node managed group (m5.xlarge)
- RDS PostgreSQL: db.r6g.large, Multi-AZ, storage encryption
- ElastiCache Redis: cache.r6g.large, cluster mode enabled
- MSK Kafka: kafka.m5.large, 3-broker cluster
- EFS: Persistent storage for Prometheus and Grafana
- ACM: TLS certificate for agridecision.ai
- Route53: DNS records for all subdomains

### 3.2 Helm Chart Deployment

```bash
# Add and update Helm repositories
helm repo add agridecision oci://registry.agridecision.ai/helm
helm repo update

# Deploy the full stack
helm upgrade --install agridecision-ai ./infrastructure/helm/agridecision-ai \
  --namespace agridecision-prod \
  --create-namespace \
  --values ./infrastructure/helm/agridecision-ai/values-production.yaml \
  --set image.tag=$(git rev-parse --short HEAD) \
  --set vault.addr=https://vault.internal.agridecision.ai
```

### 3.3 ArgoCD GitOps Setup

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy AgriDecision AI Application to ArgoCD
kubectl apply -f infrastructure/k8s/argocd/application.yaml

# Watch sync status
argocd app get agridecision-ai-production
argocd app sync agridecision-ai-production
```

**ArgoCD Application Configuration:**
```yaml
# infrastructure/k8s/argocd/application.yaml
spec:
  source:
    repoURL: 'https://github.com/agridecision/agridecision-ai.git'
    targetRevision: HEAD
    path: infrastructure/helm/agridecision-ai
    helm:
      valueFiles:
        - values-production.yaml
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### 3.4 Post-Deployment Validation

```bash
# Verify all pods are running
kubectl get pods -n agridecision-prod

# Check service endpoints
kubectl get svc -n agridecision-prod

# Run health checks
curl https://api.agridecision.ai/health
curl https://api.agridecision.ai/v1/auth/health

# Verify Kong routes
curl http://localhost:8001/services  # Kong Admin API
```

---

## 4. CI/CD Pipeline Configuration

### 4.1 GitHub Actions Workflow

**File:** `.github/workflows/agri-devops.yml`

```yaml
name: AgriDecision AI CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Python Lint (Ruff)
        run: pip install ruff && ruff check .
      - name: TypeScript Lint (ESLint)
        run: cd frontend/apps/agronomist-portal && npm ci && npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - name: Python Unit Tests
        run: python -m pytest testing/unit/ -v
      - name: React Unit Tests
        run: cd frontend/apps/agronomist-portal && npm run test
      - name: Flutter Tests
        run: cd mobile && flutter test

  build-push:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Build Docker Images
        run: docker-compose build
      - name: Push to Harbor Registry
        run: |
          docker tag agridecision/user-service:latest registry.agridecision.ai/agridecision/user-service:${{ github.sha }}
          docker push registry.agridecision.ai/agridecision/user-service:${{ github.sha }}
      - name: Sign Image (Cosign)
        run: cosign sign --key env://COSIGN_PRIVATE_KEY registry.agridecision.ai/agridecision/user-service:${{ github.sha }}

  deploy:
    runs-on: ubuntu-latest
    needs: build-push
    if: github.ref == 'refs/heads/main'
    steps:
      - name: ArgoCD Sync (Staging)
        run: argocd app sync agridecision-ai-staging --revision ${{ github.sha }}
```

---

## 5. Environment Variables Reference

### 5.1 Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://agri_user:password@agri-postgres:5432/agri_db
TIMESCALE_URL=postgresql+asyncpg://agri_user:password@agri-timescaledb:5432/agri_timeseries

# Redis
REDIS_URL=redis://agri-redis:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=agri-kafka:9092

# Vault
VAULT_ADDR=http://agri-vault:8200
VAULT_TOKEN=<dev-root-token>  # Use Vault Agent Injector in production

# JWT (Development only — use Vault in production)
JWT_PRIVATE_KEY_PATH=./certs/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./certs/jwt_public.pem

# External APIs
OPENWEATHER_API_KEY=<your_openweather_api_key>
GOOGLE_CLIENT_ID=<your_google_oauth_client_id>
APPLE_CLIENT_ID=com.agridecision.app
TWILIO_ACCOUNT_SID=<your_twilio_sid>
TWILIO_AUTH_TOKEN=<your_twilio_token>

# Triton Inference
TRITON_HOST=agri-triton
TRITON_PORT=8080
```

---

## 6. Monitoring & Observability Access

| Service | URL (Local) | URL (Production) | Credentials |
| :--- | :--- | :--- | :--- |
| Grafana | http://localhost:3000 | https://grafana.agridecision.ai | admin / admin |
| Prometheus | http://localhost:9090 | https://prometheus.agridecision.ai | None (internal) |
| Loki | http://localhost:3100 | — | Via Grafana |
| Tempo | http://localhost:3200 | — | Via Grafana |
| Vault UI | http://localhost:8200 | https://vault.agridecision.ai | Root token |
| Kong Admin | http://localhost:8001 | Internal only | None |
| ArgoCD | — | https://argocd.agridecision.ai | argocd admin |

---

## 7. Rollback Procedures

### 7.1 Helm Rollback

```bash
# List deployment history
helm history agridecision-ai -n agridecision-prod

# Rollback to previous release
helm rollback agridecision-ai -n agridecision-prod

# Or rollback to specific revision
helm rollback agridecision-ai 3 -n agridecision-prod
```

### 7.2 ArgoCD Rollback

```bash
# Rollback via ArgoCD to previous sync
argocd app rollback agridecision-ai-production <HISTORY_ID>
```

### 7.3 Database Migration Rollback

```bash
# Alembic rollback (if schema migration was part of deployment)
alembic downgrade -1
```
