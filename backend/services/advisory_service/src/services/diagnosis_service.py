"""
Advisory Service - Diagnosis Service (Business Logic)
Manages image upload registration and asynchronous ML model result processing.
"""
from uuid import UUID

from backend.common.exceptions import NotFoundException
from backend.common.logging import get_logger
from backend.services.advisory_service.src.models.image_diagnosis import ImageDiagnosis
from backend.services.advisory_service.src.repositories.diagnosis_repository import DiagnosisRepository
from backend.services.advisory_service.src.schemas.diagnosis import (
    DiagnosisStatusResponse,
    DiagnosisSubmitResponse,
)

logger = get_logger(__name__)


class DiagnosisService:
    def __init__(self, repo: DiagnosisRepository):
        self.repo = repo

    async def register_upload(
        self,
        user_id: UUID,
        plot_id: UUID | None,
        image_s3_key: str,
        content_type: str = "image/jpeg",
    ) -> DiagnosisSubmitResponse:
        """
        Register the image upload in the database with PENDING status.
        The actual ML inference is triggered asynchronously via a Kafka event
        consumed by the AI worker pod (Triton Inference Server).
        """
        diagnosis = ImageDiagnosis(
            user_id=user_id,
            plot_id=plot_id,
            image_s3_key=image_s3_key,
            image_content_type=content_type,
            model_version="plant-disease-v2.0",
            processing_status="PENDING",
        )
        saved = await self.repo.create(diagnosis)

        logger.info(
            "Image diagnosis registered",
            extra={"diagnosis_id": str(saved.id), "user_id": str(user_id)}
        )

        # TODO: Publish Kafka event to trigger AI worker
        # await publish_diagnosis_event("diagnosis.image.submitted", str(saved.id), {"s3_key": image_s3_key})

        return DiagnosisSubmitResponse(
            diagnosis_id=saved.id,
            status="PENDING",
        )

    async def get_status(self, diagnosis_id: UUID, user_id: UUID) -> DiagnosisStatusResponse:
        """Poll status of an in-progress or completed diagnosis."""
        diagnosis = await self.repo.get_by_id(diagnosis_id)

        if not diagnosis or diagnosis.user_id != user_id:
            raise NotFoundException(detail="Diagnosis not found")

        return DiagnosisStatusResponse.model_validate(diagnosis)
