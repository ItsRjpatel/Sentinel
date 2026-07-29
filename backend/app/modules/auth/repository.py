import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError as SAIntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.exceptions import (
    DuplicateEntryError,
    IntegrityError,
    NotFoundError,
)
from app.modules.auth.models import Permission, RefreshToken, Role, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> User:
        user = User(**data)
        self.session.add(user)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError(
                    "User with this username or email already exists."
                )
            raise IntegrityError(str(e.orig))
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, user: User, data: dict[str, Any]) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError(
                    "User with this username or email already exists."
                )
            raise IntegrityError(str(e.orig))
        return user

    async def soft_delete(self, user: User) -> User:
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return user

    async def exists(self, user_id: uuid.UUID) -> bool:
        stmt = select(User.id).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def count(self) -> int:
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count if count is not None else 0

    async def assign_role(self, user: User, role: Role) -> User:
        if role not in user.roles:
            user.roles.append(role)
            await self.session.flush()
        return user

    async def remove_role(self, user: User, role: Role) -> User:
        if role in user.roles:
            user.roles.remove(role)
            await self.session.flush()
        return user

    async def list_roles(self, user_id: uuid.UUID) -> Sequence[Role]:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user.roles


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Role:
        role = Role(**data)
        self.session.add(role)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError("Role with this name already exists.")
            raise IntegrityError(str(e.orig))
        return role

    async def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name, Role.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[Role]:
        stmt = select(Role).where(Role.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, role: Role, data: dict[str, Any]) -> Role:
        for key, value in data.items():
            setattr(role, key, value)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError("Role with this name already exists.")
            raise IntegrityError(str(e.orig))
        return role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
        await self.session.flush()

    async def exists(self, role_id: uuid.UUID) -> bool:
        stmt = select(Role.id).where(Role.id == role_id, Role.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def assign_permission(self, role: Role, permission: Permission) -> Role:
        if permission not in role.permissions:
            role.permissions.append(permission)
            await self.session.flush()
        return role

    async def remove_permission(self, role: Role, permission: Permission) -> Role:
        if permission in role.permissions:
            role.permissions.remove(permission)
            await self.session.flush()
        return role

    async def list_permissions(self, role_id: uuid.UUID) -> Sequence[Permission]:
        role = await self.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role not found")
        return role.permissions


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Permission:
        permission = Permission(**data)
        self.session.add(permission)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError("Permission with this name already exists.")
            raise IntegrityError(str(e.orig))
        return permission

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(
            Permission.name == name, Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, permission_id: uuid.UUID) -> Permission | None:
        stmt = select(Permission).where(
            Permission.id == permission_id, Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[Permission]:
        stmt = (
            select(Permission)
            .where(Permission.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, permission: Permission, data: dict[str, Any]) -> Permission:
        for key, value in data.items():
            setattr(permission, key, value)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError("Permission with this name already exists.")
            raise IntegrityError(str(e.orig))
        return permission

    async def delete(self, permission: Permission) -> None:
        await self.session.delete(permission)
        await self.session.flush()

    async def exists(self, permission_id: uuid.UUID) -> bool:
        stmt = select(Permission.id).where(
            Permission.id == permission_id, Permission.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.first() is not None


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> RefreshToken:
        token = RefreshToken(**data)
        self.session.add(token)
        try:
            await self.session.flush()
        except SAIntegrityError as e:
            if (
                "unique constraint" in str(e.orig).lower()
                or "duplicate key" in str(e.orig).lower()
            ):
                raise DuplicateEntryError("Refresh token already exists.")
            raise IntegrityError(str(e.orig))
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke(self, token: RefreshToken) -> RefreshToken:
        token.revoked = True
        await self.session.flush()
        return token

    async def revoke_all(self, user_id: uuid.UUID) -> None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked = True
        await self.session.flush()

    async def cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)
        stmt = delete(RefreshToken).where(RefreshToken.expiry < now)
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete(self, token: RefreshToken) -> None:
        await self.session.delete(token)
        await self.session.flush()
