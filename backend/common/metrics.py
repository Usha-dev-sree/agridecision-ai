"""
AgriDecision AI - Common Prometheus Metrics Setup
==================================================
Shared helper that wires prometheus-fastapi-instrumentator onto any
FastAPI application and exposes the /metrics endpoint Prometheus scrapes.

Usage (in each service main.py):
    from backend.common.metrics import instrument_app
    instrument_app(app)
"""
from fastapi import FastAPI


def instrument_app(app: FastAPI) -> None:
    """
    Attach Prometheus instrumentation to a FastAPI app and expose /metrics.
    Safe to call even if prometheus-fastapi-instrumentator is not installed;
    in that case the endpoint is silently skipped (no 404 flood).
    """
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=False,
            excluded_handlers=["/health", "/metrics"],
        ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    except ImportError:
        # Library not installed — serve a plain-text fallback so Prometheus
        # gets 200 instead of 404 (avoids noisy scrape errors in Grafana).
        from fastapi.responses import PlainTextResponse

        @app.get("/metrics", include_in_schema=False, tags=["System"])
        async def metrics_unavailable():
            return PlainTextResponse(
                "# prometheus-fastapi-instrumentator not installed\n",
                media_type="text/plain; version=0.0.4; charset=utf-8",
            )
