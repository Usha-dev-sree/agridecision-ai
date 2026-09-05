# Use the official Python image
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
RUN pip install poetry==1.7.1

WORKDIR /app
COPY backend/services/advisory_service/pyproject.toml backend/services/advisory_service/poetry.lock* ./
RUN poetry install --only main --no-root

# Second stage: runtime
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY backend/common/ /app/backend/common/
COPY backend/services/advisory_service/ /app/backend/services/advisory_service/
COPY ai_services/ /app/ai_services/

ENV PYTHONPATH=/app

RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

EXPOSE 8002

CMD ["uvicorn", "backend.services.advisory_service.src.main:app", "--host", "0.0.0.0", "--port", "8002"]
