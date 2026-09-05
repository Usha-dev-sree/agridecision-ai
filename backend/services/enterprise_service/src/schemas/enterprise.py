"""
Enterprise Service - Pydantic Schemas
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    tax_identifier: str = Field(..., min_length=5, max_length=50)
    tier: str = Field("ENTERPRISE_BASIC", description="ENTERPRISE_BASIC, ENTERPRISE_PRO, ENTERPRISE_CUSTOM")
    contact_email: str = Field(..., min_length=5)


class OrganizationItem(BaseModel):
    id: UUID
    name: str
    tax_identifier: str
    tier: str
    contact_email: str
    associated_farms_count: int
    created_at: datetime


class CreateContractRequest(BaseModel):
    contract_code: str = Field(..., min_length=3, max_length=50)
    contract_type: str = Field("CROP_PROCUREMENT", description="CROP_PROCUREMENT, INPUT_SUPPLY, ADVISORY_SLA")
    start_date: str
    end_date: str
    value_inr: float = Field(..., gt=0)


class ContractItem(BaseModel):
    id: UUID
    organization_id: UUID
    contract_code: str
    contract_type: str
    status: str
    start_date: str
    end_date: str
    value_inr: float
