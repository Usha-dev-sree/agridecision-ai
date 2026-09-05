"""
Advisory Service - Diagnosis Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DiagnosisClassResult(BaseModel):
    label: str
    confidence: Decimal = Field(..., ge=0, le=1)


class DiagnosisSubmitResponse(BaseModel):
    diagnosis_id: UUID
    status: str
    message: str = "Image received and queued for processing. Poll the status endpoint for results."


class DiagnosisStatusResponse(BaseModel):
    id: UUID
    plot_id: UUID | None = None
    user_id: UUID
    processing_status: str
    diagnosis_label: str | None = None
    confidence_score: Decimal | None = None
    full_diagnosis_result: list[DiagnosisClassResult] | None = None
    treatment_recommendations: dict[str, Any] | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
