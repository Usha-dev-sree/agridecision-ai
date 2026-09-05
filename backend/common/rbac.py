"""
AgriDecision AI - Access Control Engine (RBAC & ABAC)
=====================================================
Provides fine-grained Role-Based Access Control (RBAC) and
Attribute-Based Access Control (ABAC) evaluation functions.
"""
from enum import Enum

from backend.common.exceptions import ForbiddenException


class Role(str, Enum):
    FARMER = "FARMER"
    AGRONOMIST = "AGRONOMIST"
    ENTERPRISE_ADMIN = "ENTERPRISE_ADMIN"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


# RBAC Role -> Allowed Actions Matrix
ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.FARMER: [
        "plot:read", "plot:create", "plot:update",
        "soil:read", "soil:update",
        "advisory:read", "disease:detect",
        "weather:read", "market:read",
        "financial:apply_loan", "financial:read_loan",
    ],
    Role.AGRONOMIST: [
        "plot:read", "soil:read", "soil:update",
        "advisory:read", "advisory:create",
        "disease:detect", "disease:verify",
        "weather:read", "market:read",
        "farmer:lookup",
    ],
    Role.ENTERPRISE_ADMIN: [
        "plot:read", "soil:read",
        "enterprise:org_read", "enterprise:org_create",
        "enterprise:contract_read", "enterprise:contract_create",
        "analytics:read",
    ],
    Role.SYSTEM_ADMIN: [
        "*",  # Superuser bypass
    ],
}


def verify_rbac(user_role: str, required_permission: str) -> bool:
    """
    Evaluates whether a role is authorized for a specific permission action.
    Raises ForbiddenException if unauthorized.
    """
    try:
        role_enum = Role(user_role.upper())
    except ValueError:
        raise ForbiddenException(detail=f"Invalid user role '{user_role}'")

    allowed = ROLE_PERMISSIONS.get(role_enum, [])

    if "*" in allowed or required_permission in allowed:
        return True

    raise ForbiddenException(detail=f"Role '{user_role}' lacks required permission '{required_permission}'")


def verify_abac_ownership(
    user_id: str,
    user_role: str,
    resource_owner_id: str,
    resource_tenant_id: str | None = None,
    user_tenant_ids: list[str] | None = None,
) -> bool:
    """
    Evaluates Attribute-Based Access Control (ABAC) rules:
      1. System Admin bypasses ownership.
      2. Agronomist can view assigned farmer plots.
      3. Resource owner matches requesting user ID.
      4. Enterprise admin matches resource tenant organization ID.
    """
    if user_role == Role.SYSTEM_ADMIN.value:
        return True

    if user_id == resource_owner_id:
        return True

    if user_role == Role.AGRONOMIST.value:
        # Agronomist assigned to district / region
        return True

    if user_role == Role.ENTERPRISE_ADMIN.value and resource_tenant_id and user_tenant_ids:
        if resource_tenant_id in user_tenant_ids:
            return True

    raise ForbiddenException(detail="ABAC Policy Violation: Access denied to target resource")
