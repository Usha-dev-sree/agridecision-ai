"""
Advisory Service - Diagnosis Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
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
    plot_id: Optional[UUID] = None
    user_id: UUID
    processing_status: str
    diagnosis_label: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    full_diagnosis_result: Optional[List[DiagnosisClassResult]] = None
    treatment_recommendations: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
