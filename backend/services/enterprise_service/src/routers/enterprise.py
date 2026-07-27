"""
Enterprise Service - FastAPI Router
"""
from typing import List

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.enterprise_service.src.dependencies import get_current_user, get_db, get_redis
from backend.services.enterprise_service.src.schemas.enterprise import (
    ContractItem,
    CreateContractRequest,
    CreateOrganizationRequest,
    OrganizationItem,
)
from backend.services.enterprise_service.src.services.enterprise_service import EnterpriseService

router = APIRouter(prefix="/v1/enterprise", tags=["Enterprise B2B"])


@router.get("/organizations", response_model=List[OrganizationItem])
async def get_organizations(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """List corporate B2B organizations (Admin/Enterprise role required)."""
    service = EnterpriseService(db, redis)
    return await service.get_organizations()


@router.post("/organizations", response_model=OrganizationItem, status_code=status.HTTP_201_CREATED)
async def create_organization(
    req: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Register a new enterprise B2B organization."""
    service = EnterpriseService(db, redis)
    return await service.create_organization(req)


@router.get("/organizations/{org_id}/contracts", response_model=List[ContractItem])
async def get_organization_contracts(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Retrieve corporate contracts and procurement SLA agreements."""
    service = EnterpriseService(db, redis)
    return await service.get_contracts(org_id)


@router.post(
    "/organizations/{org_id}/contracts",
    response_model=ContractItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_contract(
    org_id: str,
    req: CreateContractRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user_payload: dict = Depends(get_current_user),
):
    """Create a new procurement or advisory contract for an organization."""
    service = EnterpriseService(db, redis)
    return await service.create_contract(org_id, req)
