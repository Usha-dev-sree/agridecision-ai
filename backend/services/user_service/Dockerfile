# Use the official Python image
FROM python:3.11-slim as builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
RUN pip install poetry==1.7.1

WORKDIR /app

# Copy dependency files
COPY backend/services/user_service/pyproject.toml backend/services/user_service/poetry.lock* ./

# Install dependencies
RUN poetry install --only main --no-root

# Second stage: runtime
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy common package and service code
# Assuming context is the repo root
COPY backend/common/ /app/backend/common/
COPY backend/services/user_service/ /app/backend/services/user_service/

# Set Python path to find the modules
ENV PYTHONPATH=/app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

EXPOSE 8000

# Start the service
CMD ["uvicorn", "backend.services.user_service.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
