FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

WORKDIR /app

# Copy and install dependencies (cache layer)
COPY backend/services/${SERVICE}/pyproject.toml ./
COPY backend/services/${SERVICE}/requirements.txt ./
RUN uv pip install --system -r requirements.txt

# ─────────────────────────────────────────────────────────
# Runtime Stage — Slim final image
# ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY backend/services/${SERVICE}/src ./src
COPY backend/common ./common

# Set ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz/liveness || exit 1

# Start Uvicorn with production settings
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--log-level", "info"]
