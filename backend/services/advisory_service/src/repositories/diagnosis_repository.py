"""
Advisory Service - Diagnosis Repository
Handles persistence of image diagnosis records.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.advisory_service.src.models.image_diagnosis import ImageDiagnosis


class DiagnosisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, diagnosis: ImageDiagnosis) -> ImageDiagnosis:
        self.session.add(diagnosis)
        await self.session.flush()
        return diagnosis

    async def get_by_id(self, diagnosis_id: UUID) -> Optional[ImageDiagnosis]:
        stmt = select(ImageDiagnosis).where(ImageDiagnosis.id == diagnosis_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_result(
        self,
        diagnosis: ImageDiagnosis,
        diagnosis_label: str,
        confidence_score: float,
        full_result: dict,
        treatment_recommendations: dict,
    ) -> ImageDiagnosis:
        from datetime import datetime, timezone
        diagnosis.diagnosis_label = diagnosis_label
        diagnosis.confidence_score = confidence_score
        diagnosis.full_diagnosis_result = full_result
        diagnosis.treatment_recommendations = treatment_recommendations
        diagnosis.processing_status = "COMPLETED"
        diagnosis.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return diagnosis
