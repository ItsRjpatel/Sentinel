import uuid
from typing import Optional, List, Tuple, Dict
from datetime import datetime, timezone
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import User, Role, UserRole

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        stmt = select(User)

        if status and status.upper() != "ALL":
            if status.upper() == "ACTIVE":
                stmt = stmt.where(User.is_active == True)
            elif status.upper() == "DISABLED":
                stmt = stmt.where(User.is_active == False)
            elif status.upper() == "LOCKED":
                now_utc = datetime.now(timezone.utc)
                stmt = stmt.where(User.locked_until > now_utc)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar() or 0

        # Pagination & Ordering
        offset = (page - 1) * page_size
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)

        res = await self.db.execute(stmt)
        users = list(res.scalars().all())
        return users, total

    async def get_summary_counts(self) -> Dict[str, int]:
        stmt = select(User)
        res = await self.db.execute(stmt)
        users = list(res.scalars().all())

        now_utc = datetime.now(timezone.utc)
        counts = {
            "total": len(users),
            "online": 0,
            "disabled": 0,
            "locked": 0,
            "administrators": 0,
            "analysts": 0,
            "agents": 0,
            "guests": 0,
        }

        for u in users:
            if not u.is_active:
                counts["disabled"] += 1
            if u.locked_until and u.locked_until > now_utc:
                counts["locked"] += 1

            role_names = [r.name.lower() for r in (u.roles or [])]
            if any("admin" in r for r in role_names):
                counts["administrators"] += 1
            elif any("analyst" in r for r in role_names):
                counts["analysts"] += 1
            elif any("agent" in r for r in role_names):
                counts["agents"] += 1
            else:
                counts["guests"] += 1

            if u.last_login and (now_utc - u.last_login).total_seconds() < 86400:
                counts["online"] += 1

        return counts
