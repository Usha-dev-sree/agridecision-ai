# ── Notification Service Dockerfile ───────────────────────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/services/notification_service/pyproject.toml ./
RUN pip install --no-cache-dir .

# ── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/services/notification_service/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy common package and service code (build context = repo root)
COPY backend/common/ /app/backend/common/
COPY backend/services/notification_service/ /app/backend/services/notification_service/

ENV PYTHONPATH=/app

RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

EXPOSE 8007

CMD ["uvicorn", "backend.services.notification_service.src.main:app", "--host", "0.0.0.0", "--port", "8007"]
