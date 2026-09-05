# ── Market Service Dockerfile ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/services/market_service/pyproject.toml ./
RUN pip install --no-cache-dir build && pip install --no-cache-dir .

# ── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Re-install in runtime (pip install is fast for these simple deps)
COPY backend/services/market_service/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy common package and service code (build context = repo root)
COPY backend/common/ /app/backend/common/
COPY backend/services/market_service/ /app/backend/services/market_service/

ENV PYTHONPATH=/app

RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

EXPOSE 8004

CMD ["uvicorn", "backend.services.market_service.src.main:app", "--host", "0.0.0.0", "--port", "8004"]
