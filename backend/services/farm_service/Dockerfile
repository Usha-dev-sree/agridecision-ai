# Use the official Python image
FROM python:3.11-slim as builder

# Install system dependencies required for building Python packages and PostGIS dependencies (GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
RUN pip install poetry==1.7.1

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only main --no-root

# Second stage: runtime
FROM python:3.11-slim

# Install runtime spatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgeos-c1v5 \
    libproj22 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy common package and service code
COPY backend/common/ /app/backend/common/
COPY backend/services/farm_service/ /app/backend/services/farm_service/

# Set Python path to find the modules
ENV PYTHONPATH=/app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

EXPOSE 8001

# Start the service
CMD ["uvicorn", "backend.services.farm_service.src.main:app", "--host", "0.0.0.0", "--port", "8001"]
