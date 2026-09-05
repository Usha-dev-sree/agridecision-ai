"""
AgriDecision AI - Common Security Middleware
============================================
Provides:
  - SecurityHeadersMiddleware: injects OWASP-recommended security headers on every response
  - RequestSizeLimitMiddleware: rejects bodies exceeding the configured limit (DoS prevention)
  - CorrelationIdMiddleware: propagates X-Request-ID for distributed tracing
"""
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Default max body = 10 MB (protects against SSRF/DoS via large payloads)
_DEFAULT_MAX_BODY_BYTES: int = 10 * 1024 * 1024  # 10 MB


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects OWASP-recommended HTTP security headers on every response.

    Headers injected:
      - X-Content-Type-Options: nosniff            (prevents MIME-type sniffing → XSS vector)
      - X-Frame-Options: DENY                       (prevents clickjacking)
      - X-XSS-Protection: 0                         (modern: disable legacy XSS auditor, rely on CSP)
      - Referrer-Policy: strict-origin-when-cross   (limits referrer leakage)
      - Content-Security-Policy                     (restricts content sources → XSS prevention)
      - Strict-Transport-Security                   (HSTS — enforces TLS)
      - Permissions-Policy                          (disables unused browser features)
      - Cache-Control: no-store                     (prevents caching of sensitive API responses)
    """

    # Doc UI paths — Swagger UI and ReDoc need relaxed CSP to load JS/CSS
    _DOC_PATHS = {"/v1/docs", "/docs", "/redoc", "/v1/redoc"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        content_type = response.headers.get("content-type", "")
        is_html_doc = (
            "text/html" in content_type
            and request.url.path in self._DOC_PATHS
        )

        # XSS / Content Sniffing Prevention
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if is_html_doc:
            # ── Swagger / ReDoc pages need scripts, styles, and CDN resources ──
            # Allow self-hosted assets AND jsdelivr CDN (Swagger UI bundles).
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            # Allow iframes in doc pages (Swagger UI uses them internally)
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            # ── Strict policy for all JSON API responses ──
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; "
                "frame-ancestors 'none'; "
                "form-action 'none';"
            )
            response.headers["X-Frame-Options"] = "DENY"

        # HSTS — enforce TLS for 1 year (includeSubDomains + preload for production)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Disable unused browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        # No caching for API responses (relax for doc assets so Swagger UI loads fast)
        if is_html_doc:
            response.headers["Cache-Control"] = "no-cache"
        else:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        # Remove server fingerprinting header if set by upstream
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests whose Content-Length exceeds ``max_body_bytes``.
    Provides protection against:
      - SSRF via oversized proxy payloads
      - DoS via large JSON/multipart bodies
    """

    def __init__(self, app, max_body_bytes: int = _DEFAULT_MAX_BODY_BYTES):
        super().__init__(app)
        self.max_body_bytes = max_body_bytes

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_bytes:
            return Response(
                content='{"type":"https://api.agridecision.com/errors/payload-too-large",'
                        '"title":"Payload Too Large",'
                        f'"status":413,'
                        '"detail":"Request body exceeds the maximum allowed size."}',
                status_code=413,
                media_type="application/problem+json",
            )
        return await call_next(request)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Propagates or generates an X-Request-ID header for distributed tracing.
    The ID is echoed back in the response for client-side correlation.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Inject into request state for access in route handlers/logs
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
