# AgriDecision AI — Developer Makefile
# =============================================

.PHONY: help setup lint test migrate seed docker-build docker-push clean

help:
	@echo "AgriDecision AI — Developer Commands"
	@echo "======================================"
	@echo "  make setup          Install all dependencies"
	@echo "  make lint           Run Ruff + mypy across all backend services"
	@echo "  make test           Run full pytest integration test suite"
	@echo "  make migrate        Apply Alembic migrations (set SERVICE= env var)"
	@echo "  make seed           Seed reference data into local database"
	@echo "  make docker-build   Build all service Docker images"
	@echo "  make docker-push    Push all images to Harbor registry"
	@echo "  make k8s-staging    Sync ArgoCD staging applications"
	@echo "  make clean          Remove build artifacts and __pycache__"

setup:
	pip install uv
	uv pip install -r backend/services/user-service/requirements.txt
	npm install

lint:
	ruff check backend/
	mypy backend/services/user-service/src
	mypy backend/services/advisory-service/src
	mypy backend/services/farm-service/src

test:
	pytest testing/integration/ -v --tb=short
	pytest testing/contract/ -v

migrate:
	@echo "Running Alembic upgrade on service: $(SERVICE)"
	cd backend/services/$(SERVICE) && alembic upgrade head

seed:
	psql -h localhost -U agridecision -d agridecision -f database/postgresql/seed_data/crops_catalogue.sql
	psql -h localhost -U agridecision -d agridecision -f database/postgresql/seed_data/aez_zones.sql
	psql -h localhost -U agridecision -d agridecision -f database/postgresql/seed_data/mandi_directory.sql

docker-build:
	docker build -f devops/docker/backend.Dockerfile -t harbor.agridecision.ai/core/user-service:dev .
	docker build -f devops/docker/backend.Dockerfile -t harbor.agridecision.ai/core/farm-service:dev .
	docker build -f devops/docker/advisory.Dockerfile -t harbor.agridecision.ai/advisory/advisory-service:dev .

docker-push:
	docker push harbor.agridecision.ai/core/user-service:dev
	docker push harbor.agridecision.ai/core/farm-service:dev
	docker push harbor.agridecision.ai/advisory/advisory-service:dev

k8s-staging:
	argocd app sync agridecision-staging --prune

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
