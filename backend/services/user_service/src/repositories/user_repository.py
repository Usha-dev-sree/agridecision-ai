"""
User Service - User Repository
Handles database operations for iam.user and iam.user_profile.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.user_service.src.models.user import User, UserProfile
from backend.services.user_service.src.schemas.user import UserBase, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_phone(self, phone_number: str) -> Optional[User]:
        stmt = select(User).where(User.phone_number == phone_number).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, phone_number: str, data: UserBase) -> User:
        user = User(
            phone_number=phone_number,
            full_name=data.full_name,
            email=data.email,
            preferred_language=data.preferred_language,
            state_code=data.state_code,
            district_name=data.district_name,
            farmer_type=data.farmer_type,
            has_verified_phone=True,
            account_status="ACTIVE"
        )
        profile = UserProfile(user=user)
        self.session.add(user)
        self.session.add(profile)
        await self.session.flush()
        return user

    async def update_user(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True, exclude={"profile"})
        for key, value in update_data.items():
            setattr(user, key, value)
            
        if data.profile and user.profile:
            profile_data = data.profile.model_dump(exclude_unset=True)
            for key, value in profile_data.items():
                setattr(user.profile, key, value)
                
        await self.session.flush()
        return user
