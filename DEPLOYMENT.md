# AgriDecision AI — Production Deployment Guide

This guide details the automated zero-downtime deployment, infrastructure setup, health checks, rollback procedures, and disaster recovery for **AgriDecision AI**.

---

## 🏗️ 1. Infrastructure Architecture

The production architecture deploys to **Amazon Web Services (AWS)** using Kubernetes (AWS EKS), Terraform, and ArgoCD GitOps:

- **Cluster:** Amazon EKS (`v1.27`) with managed node groups.
- **Databases:**
  - Amazon RDS PostgreSQL 15 (User auth, financial applications, organization multi-tenancy).
  - TimescaleDB (Plot GIS boundaries, IoT time-series sensor readings, soil profiles).
  - Amazon ElastiCache Redis 7 (Token blacklisting, mandi price caching, sliding window rate limiting).
- **Event Bus:** Amazon Managed Streaming for Apache Kafka (MSK).
- **API Gateway:** Kong API Gateway (`:8000`) with TLS 1.3 termination and CORS policies.
- **Observability:** Prometheus, Grafana, Loki (log aggregation), and Tempo (distributed tracing).

---

## 🚀 2. Pre-Deployment Setup & Verification

### Step A: Apply Infrastructure with Terraform
```bash
cd infrastructure/terraform/environments/production
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### Step B: Configure Kubeconfig & Secrets
```bash
aws eks update-kubeconfig --region us-east-1 --name agri-prod-eks
kubectl create namespace agridecision
kubectl create secret generic agridecision-secrets --from-env-file=.env.production -n agridecision
```

---

## 🔁 3. Automated Canary Release Pipeline (GitHub Actions & ArgoCD)

Deployments are automatically triggered on Git tag releases (`v*.*.*`):

```bash
git tag -a v1.0.0 -m "Production Release 1.0.0"
git push origin v1.0.0
```

### Canary Rollout Sequence:
1. **Security Gate:** Cosign image signature verification and Trivy vulnerability scan.
2. **5% Traffic Canary:** Deploys new version to $5\%$ of pod traffic; monitors error rates for 10 minutes.
3. **Automated Rollback Check:** If HTTP 5xx error rate exceeds $1.0\%$, ArgoCD automatically triggers instant rollback (`argocd app rollback`).
4. **50% Traffic Promotion:** Promotes canary traffic weight to $50\%$.
5. **100% Full Traffic Rollout:** Promotes to full production traffic and executes automated smoke tests.

---

## 🩺 4. Health Check Endpoints

Every microservice exposes standardized health and readiness endpoints for Kubernetes liveness/readiness probes:

- `GET /health/live` — Returns `{"status": "HEALTHY"}` if the process is responsive.
- `GET /health/ready` — Returns `{"status": "READY", "database": "CONNECTED", "redis": "CONNECTED"}`.

### Manual Smoke Test Execution:
```bash
bash scripts/ops/smoke_test.sh
```

---

## ↩️ 5. Automated & Manual Rollback Strategy

### Automated Rollback:
The canary deployment pipeline automatically executes `argocd app rollback` if Prometheus metric `rate(http_requests_total{status=~'5..'}[5m])` exceeds $1.0\%$.

### Manual Emergency Rollback Command:
```bash
# Rollback ArgoCD production application to previous GitOps revision
argocd app rollback agridecision-production

# Or using kubectl rollback
kubectl rollout undo deployment/user-service -n agridecision
kubectl rollout undo deployment/farm-service -n agridecision
kubectl rollout undo deployment/advisory-service -n agridecision
```

---

## 📊 6. Monitoring & Alerting

- **Grafana Dashboard URL:** `https://grafana.agridecision.ai`
- **Prometheus Metrics Endpoint:** `http://prometheus.agridecision.internal:9090`
- **Slack Alerting Channel:** `#alerts-agri-production`

Key Alerts Configured:
- `High5xxErrorRate`: Triggers when 5xx errors $> 1.0\%$ over 5 minutes.
- `HighLatencyP99`: Triggers when P99 response time $> 500\text{ ms}$.
- `RedisConnectionPoolExhausted`: Triggers when available Redis connections $< 5\%$.
