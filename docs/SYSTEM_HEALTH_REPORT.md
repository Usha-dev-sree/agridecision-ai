# AgriDecision AI — System Health Report

## Container & Infrastructure Health

| Service Name | Image | Status | Port Binding |
| :--- | :--- | :---: | :--- |
| `agri-postgres` | `postgis/postgis:15-3.4-alpine` | `HEALTHY` | 5423:5432 |
| `agri-timescaledb` | `timescale/timescaledb-ha:pg15` | `HEALTHY` | 5433:5432 |
| `agri-redis` | `redis:7-alpine` | `HEALTHY` | 6379:6379 |
| `agri-zookeeper` | `confluentinc/cp-zookeeper:7.3.0` | `HEALTHY` | 2181:2181 |
| `agri-kafka` | `confluentinc/cp-kafka:7.3.0` | `HEALTHY` | 9092:9092 |
| `agri-kong` | `kong:3.2-alpine` | `HEALTHY` | 8000:8000 / 8001:8001 |
| `agri-prometheus` | `prom/prometheus:v2.43.0` | `HEALTHY` | 9090:9090 |
| `agri-grafana` | `grafana/grafana:9.5.2` | `HEALTHY` | 3000:3000 |
| `agri-loki` | `grafana/loki:2.8.0` | `HEALTHY` | 3100:3100 |
| `agri-tempo` | `grafana/tempo:2.1.0` | `HEALTHY` | 3200:3200 |
| `agri-vault` | `hashicorp/vault:1.13.1` | `HEALTHY` | 8200:8200 |
