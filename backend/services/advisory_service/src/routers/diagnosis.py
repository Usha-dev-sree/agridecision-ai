"""
Advisory Service - Diagnosis Router
Handles image upload registration and asynchronous diagnosis polling.
"""
import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.logging import get_logger
from backend.services.advisory_service.src.dependencies import get_current_user, get_db
from backend.services.advisory_service.src.repositories.diagnosis_repository import DiagnosisRepository
from backend.services.advisory_service.src.schemas.diagnosis import (
    DiagnosisStatusResponse,
    DiagnosisSubmitResponse,
)
from backend.services.advisory_service.src.services.diagnosis_service import DiagnosisService

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/advisory/diagnosis", tags=["Disease Diagnosis"])


def get_diagnosis_service(session: AsyncSession = Depends(get_db)) -> DiagnosisService:
    repo = DiagnosisRepository(session)
    return DiagnosisService(repo)


@router.post("", response_model=DiagnosisSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_image_for_diagnosis(
    plot_id: Optional[UUID] = Form(None),
    file: UploadFile = File(..., description="Plant leaf or crop image (JPEG/PNG)"),
    current_user: dict = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """
    Submit a plant image for AI-powered disease diagnosis.
    Returns a diagnosis_id to poll for results asynchronously.
    The image is stored in S3 and the diagnosis runs asynchronously.
    """
    user_id = UUID(current_user["sub"])

    # Build a deterministic S3 key from user_id + filename
    s3_key = f"diagnoses/{user_id}/{file.filename}"
    content_type = file.content_type or "image/jpeg"

    # Upload to S3 via aioboto3 (degrades gracefully if unconfigured in dev)
    bucket_name = os.getenv("S3_BUCKET_NAME", "agridecision-diagnoses")
    try:
        import aioboto3
        session = aioboto3.Session()
        async with session.client("s3") as s3:
            file.file.seek(0)
            await s3.upload_fileobj(
                file.file,
                bucket_name,
                s3_key,
                ExtraArgs={"ContentType": content_type},
            )
            logger.info("Image uploaded to S3", extra={"bucket": bucket_name, "key": s3_key})
    except Exception as exc:
        logger.warning(
            "S3 upload skipped (S3 unavailable or not configured)",
            extra={"error": str(exc)},
        )

    return await service.register_upload(
        user_id=user_id,
        plot_id=plot_id,
        image_s3_key=s3_key,
        content_type=content_type,
    )


@router.get("/{diagnosis_id}", response_model=DiagnosisStatusResponse)
async def get_diagnosis_status(
    diagnosis_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """Poll the status and results of an image diagnosis."""
    user_id = UUID(current_user["sub"])
    return await service.get_status(diagnosis_id, user_id)
