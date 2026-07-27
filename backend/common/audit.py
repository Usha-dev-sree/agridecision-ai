"""
AgriDecision AI - Security Audit Logging Engine
===============================================
Writes structured, immutable security audit event records (login attempts, privilege changes, PII access).
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.common.logging import get_logger

logger = get_logger("security.audit")


class AuditLogger:
    """Security audit logger emitting JSON audit events for compliance (SOC 2, ISO 27001)."""

    @staticmethod
    def log_event(
        action: str,
        actor_id: str,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emits a structured audit log entry."""
        audit_entry = {
            "event_type": "AUDIT_LOG",
            "action": action,
            "actor_id": actor_id,
            "resource_id": resource_id,
            "status": status,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        logger.info("Security Audit Event: %s", action, extra=audit_entry)
