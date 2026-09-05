"""
User Service - Users Router
Endpoints for user profile retrieval and updates.
"""
from uuid import UUID

from backend.services.user_service.src.dependencies import get_current_user, get_db
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.user import UserDetailResponse, UserUpdate
from backend.services.user_service.src.services.user_service import UserService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    user_repo = UserRepository(session)
    return UserService(user_repo)


@router.get("/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user_payload: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the profile of the currently authenticated user."""
    user_id = UUID(current_user_payload["sub"])
    return await user_service.get_user_by_id(user_id)


@router.put("/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user_payload: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update the profile of the currently authenticated user."""
    user_id = UUID(current_user_payload["sub"])
    return await user_service.update_user(user_id, update_data)
