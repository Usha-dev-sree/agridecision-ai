"""
Enterprise Service - Business Logic Service
Provides multi-tenant organization and contract management backed by PostgreSQL.
"""
import json
import uuid
from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exceptions import ConflictException, NotFoundException
from backend.common.logging import get_logger
from backend.services.enterprise_service.src.schemas.enterprise import (
    ContractItem,
    CreateContractRequest,
    CreateOrganizationRequest,
    OrganizationItem,
)

logger = get_logger(__name__)

ORG_CACHE_PREFIX = "enterprise:org"
ORG_LIST_CACHE_KEY = "enterprise:org_list"
CACHE_TTL = 1800  # 30 minutes


class EnterpriseService:
    """Multi-tenant organization and contract management."""

    def __init__(self, db: AsyncSession, redis: Redis | None = None):
        self._db = db
        self._redis = redis

    # ── Organizations ──────────────────────────────────────────────────────────

    async def get_organizations(self) -> list[OrganizationItem]:
        """List all enterprise B2B organizations with Redis caching."""
        # Check cache
        if self._redis:
            cached = await self._redis.get(ORG_LIST_CACHE_KEY)
            if cached:
                return [OrganizationItem(**o) for o in json.loads(cached)]

        result = await self._db.execute(
            text("""
                SELECT o.id, o.name, o.tax_identifier, o.tier, o.contact_email, o.created_at,
                       COALESCE(fc.farm_count, 0) AS associated_farms_count
                FROM organizations o
                LEFT JOIN (
                    SELECT organization_id, COUNT(*) AS farm_count
                    FROM organization_farms
                    GROUP BY organization_id
                ) fc ON fc.organization_id = o.id
                ORDER BY o.created_at DESC
            """)
        )
        rows = result.fetchall()

        items = [
            OrganizationItem(
                id=UUID(str(row.id)),
                name=row.name,
                tax_identifier=row.tax_identifier,
                tier=row.tier,
                contact_email=row.contact_email,
                associated_farms_count=int(row.associated_farms_count),
                created_at=row.created_at,
            )
            for row in rows
        ]

        # Populate cache
        if self._redis:
            serialized = json.dumps([item.model_dump(mode="json") for item in items])
            await self._redis.set(ORG_LIST_CACHE_KEY, serialized, ex=CACHE_TTL)

        return items

    async def create_organization(self, req: CreateOrganizationRequest) -> OrganizationItem:
        """Register a new enterprise B2B organization."""
        # Check for duplicate tax ID
        existing = await self._db.execute(
            text("SELECT id FROM organizations WHERE tax_identifier = :tax_id"),
            {"tax_id": req.tax_identifier},
        )
        if existing.fetchone():
            raise ConflictException(detail=f"Organization with tax ID {req.tax_identifier} already exists")

        org_id = uuid.uuid4()
        now = datetime.now(UTC)

        await self._db.execute(
            text("""
                INSERT INTO organizations (id, name, tax_identifier, tier, contact_email, created_at)
                VALUES (:id, :name, :tax_id, :tier, :email, :created_at)
            """),
            {
                "id": str(org_id),
                "name": req.name,
                "tax_id": req.tax_identifier,
                "tier": req.tier,
                "email": req.contact_email,
                "created_at": now,
            },
        )
        await self._db.commit()

        # Invalidate org list cache
        if self._redis:
            await self._redis.delete(ORG_LIST_CACHE_KEY)

        logger.info("Organization created", extra={"org_id": str(org_id), "name": req.name})

        return OrganizationItem(
            id=org_id,
            name=req.name,
            tax_identifier=req.tax_identifier,
            tier=req.tier,
            contact_email=req.contact_email,
            associated_farms_count=0,
            created_at=now,
        )

    # ── Contracts ──────────────────────────────────────────────────────────────

    async def get_contracts(self, org_id: str) -> list[ContractItem]:
        """Get corporate procurement and advisory SLA contracts."""
        cache_key = f"{ORG_CACHE_PREFIX}:{org_id}:contracts"

        if self._redis:
            cached = await self._redis.get(cache_key)
            if cached:
                return [ContractItem(**c) for c in json.loads(cached)]

        result = await self._db.execute(
            text("""
                SELECT id, organization_id, contract_code, contract_type, status,
                       start_date, end_date, value_inr
                FROM enterprise_contracts
                WHERE organization_id = :org_id
                ORDER BY start_date DESC
            """),
            {"org_id": org_id},
        )
        rows = result.fetchall()

        items = [
            ContractItem(
                id=UUID(str(row.id)),
                organization_id=UUID(str(row.organization_id)),
                contract_code=row.contract_code,
                contract_type=row.contract_type,
                status=row.status,
                start_date=str(row.start_date),
                end_date=str(row.end_date),
                value_inr=float(row.value_inr),
            )
            for row in rows
        ]

        if self._redis:
            serialized = json.dumps([item.model_dump(mode="json") for item in items])
            await self._redis.set(cache_key, serialized, ex=CACHE_TTL)

        return items

    async def create_contract(self, org_id: str, req: CreateContractRequest) -> ContractItem:
        """Create a new procurement or advisory contract."""
        # Verify organization exists
        org_result = await self._db.execute(
            text("SELECT id FROM organizations WHERE id = :org_id"),
            {"org_id": org_id},
        )
        if not org_result.fetchone():
            raise NotFoundException(detail=f"Organization {org_id} not found")

        # Check for duplicate contract code
        dup_result = await self._db.execute(
            text("SELECT id FROM enterprise_contracts WHERE contract_code = :code"),
            {"code": req.contract_code},
        )
        if dup_result.fetchone():
            raise ConflictException(detail=f"Contract code {req.contract_code} already exists")

        contract_id = uuid.uuid4()

        await self._db.execute(
            text("""
                INSERT INTO enterprise_contracts
                    (id, organization_id, contract_code, contract_type, status, start_date, end_date, value_inr)
                VALUES (:id, :org_id, :code, :type, 'ACTIVE', :start, :end, :value)
            """),
            {
                "id": str(contract_id),
                "org_id": org_id,
                "code": req.contract_code,
                "type": req.contract_type,
                "start": req.start_date,
                "end": req.end_date,
                "value": req.value_inr,
            },
        )
        await self._db.commit()

        # Invalidate contracts cache
        if self._redis:
            await self._redis.delete(f"{ORG_CACHE_PREFIX}:{org_id}:contracts")

        logger.info("Contract created", extra={"contract_id": str(contract_id), "org_id": org_id})

        return ContractItem(
            id=contract_id,
            organization_id=UUID(org_id),
            contract_code=req.contract_code,
            contract_type=req.contract_type,
            status="ACTIVE",
            start_date=req.start_date,
            end_date=req.end_date,
            value_inr=req.value_inr,
        )
