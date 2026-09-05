"""
User Service - User Service (Business Logic)
Handles business logic for retrieving and updating users.
"""
from uuid import UUID

from backend.common.exceptions import NotFoundException
from backend.services.user_service.src.repositories.user_repository import UserRepository
from backend.services.user_service.src.schemas.user import UserDetailResponse, UserUpdate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: UUID) -> UserDetailResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail="User not found")
        return UserDetailResponse.model_validate(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserDetailResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail="User not found")
            
        updated_user = await self.user_repo.update_user(user, data)
        return UserDetailResponse.model_validate(updated_user)
