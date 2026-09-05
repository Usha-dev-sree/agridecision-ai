"""
AgriDecision AI - Common Exception Handlers
Implements RFC 7807 Problem Details for HTTP APIs.
"""
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class APIException(Exception):
    """Base exception for all API errors following RFC 7807."""
    def __init__(
        self,
        status_code: int,
        type_uri: str,
        title: str,
        detail: str,
        instance: str | None = None,
        extensions: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.type_uri = type_uri
        self.title = title
        self.detail = detail
        self.instance = instance
        self.extensions = extensions or {}
        super().__init__(detail)

    def to_dict(self) -> dict[str, Any]:
        """Convert to RFC 7807 dictionary."""
        response = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if self.instance:
            response["instance"] = self.instance
        if self.extensions:
            response.update(self.extensions)
        return response


class NotFoundException(APIException):
    """Resource not found exception (404)."""
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            status_code=404,
            type_uri="https://api.agridecision.com/errors/not-found",
            title="Resource Not Found",
            detail=detail,
            instance=instance,
        )


class ValidationException(APIException):
    """Validation exception (422)."""
    def __init__(self, detail: str, errors: list, instance: str | None = None):
        super().__init__(
            status_code=422,
            type_uri="https://api.agridecision.com/errors/validation-error",
            title="Validation Error",
            detail=detail,
            instance=instance,
            extensions={"errors": errors},
        )


class UnauthorizedException(APIException):
    """Unauthorized exception (401)."""
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            status_code=401,
            type_uri="https://api.agridecision.com/errors/unauthorized",
            title="Unauthorized",
            detail=detail,
            instance=instance,
        )


class ForbiddenException(APIException):
    """Forbidden exception (403)."""
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            status_code=403,
            type_uri="https://api.agridecision.com/errors/forbidden",
            title="Forbidden",
            detail=detail,
            instance=instance,
        )


class ConflictException(APIException):
    """Conflict exception (409)."""
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            status_code=409,
            type_uri="https://api.agridecision.com/errors/conflict",
            title="Resource Conflict",
            detail=detail,
            instance=instance,
        )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """FastAPI exception handler for APIException."""
    if not exc.instance:
        exc.instance = str(request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers={"Content-Type": "application/problem+json"},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled exceptions."""
    error = APIException(
        status_code=500,
        type_uri="https://api.agridecision.com/errors/internal-server-error",
        title="Internal Server Error",
        detail="An unexpected error occurred while processing the request.",
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=500,
        content=error.to_dict(),
        headers={"Content-Type": "application/problem+json"},
    )
