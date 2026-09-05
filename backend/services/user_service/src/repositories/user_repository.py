"""
User Service - User Repository
Handles database operations for iam.user and iam.user_profile.
"""
from uuid import UUID

from backend.services.user_service.src.models.user import User, UserProfile
from backend.services.user_service.src.schemas.user import UserBase, UserUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_phone(self, phone_number: str) -> User | None:
        stmt = select(User).where(User.phone_number == phone_number).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Look up user by phone number or email."""
        stmt = select(User).where((User.phone_number == identifier) | (User.email == identifier)).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
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
        await self.session.commit()
        return user

    async def create_user_with_password(
        self,
        full_name: str,
        phone_number: str,
        email: str | None,
        password_hash: str,
        role: str = "FARMER",
        state_code: str = "IN-MH",
        district_name: str | None = None,
        farmer_type: str | None = "SMALL_COMMERCIAL",
        preferred_language: str = "en"
    ) -> User:
        user = User(
            phone_number=phone_number,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            state_code=state_code,
            district_name=district_name,
            farmer_type=farmer_type,
            preferred_language=preferred_language,
            has_verified_phone=True,
            account_status="ACTIVE"
        )
        profile = UserProfile(user=user)
        self.session.add(user)
        self.session.add(profile)
        await self.session.flush()
        await self.session.commit()
        return user

    async def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        await self.session.flush()
        await self.session.commit()
        return user

    async def set_email_verified(self, user: User, status: bool = True) -> User:
        user.has_verified_email = status
        await self.session.flush()
        await self.session.commit()
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
        await self.session.commit()
        return user
