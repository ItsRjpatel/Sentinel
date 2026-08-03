import uuid
from typing import Optional, List, Tuple, Dict
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.users.repository import UserRepository
from app.modules.auth.models import User, Role, UserRole
from app.core.security import get_password_hash
from app.modules.users.schemas import UserCreateRequest, UserUpdateRequest

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def list_users_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        return await self.repo.list_paginated(page=page, page_size=page_size, search=search, role=role, status=status)

    async def get_summary(self) -> Dict[str, int]:
        return await self.repo.get_summary_counts()

    async def get_user(self, user_id: uuid.UUID) -> User:
        u = await self.repo.get_by_id(user_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return u

    async def create_user(self, req: UserCreateRequest) -> User:
        existing = await self.repo.get_by_username(req.username)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        new_user = User(
            username=req.username,
            email=req.email,
            password_hash=get_password_hash(req.password),
            first_name=req.first_name,
            last_name=req.last_name,
            phone=req.phone,
            is_active=True,
            is_verified=True,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: uuid.UUID, req: UserUpdateRequest) -> User:
        u = await self.get_user(user_id)
        if req.email is not None:
            u.email = req.email
        if req.first_name is not None:
            u.first_name = req.first_name
        if req.last_name is not None:
            u.last_name = req.last_name
        if req.phone is not None:
            u.phone = req.phone
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def enable_user(self, user_id: uuid.UUID) -> User:
        u = await self.get_user(user_id)
        u.is_active = True
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def disable_user(self, user_id: uuid.UUID) -> User:
        u = await self.get_user(user_id)
        u.is_active = False
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def unlock_user(self, user_id: uuid.UUID) -> User:
        u = await self.get_user(user_id)
        u.locked_until = None
        u.failed_login_attempts = 0
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def reset_password(self, user_id: uuid.UUID, new_pass: str) -> User:
        u = await self.get_user(user_id)
        u.password_hash = get_password_hash(new_pass)
        await self.db.commit()
        await self.db.refresh(u)
        return u

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        u = await self.get_user(user_id)
        await self.db.delete(u)
        await self.db.commit()
        return True
