import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AccountLockedError, InactiveUserError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.auth.exceptions import (
    InvalidCredentialsError,
    NotFoundError,
    UnauthorizedError,
)
from app.modules.auth.models import User
from app.modules.auth.repository import (
    PermissionRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)


def _hash_refresh_token(raw_token: str) -> str:
    """Returns SHA-256 hex digest of raw_token for deterministic DB lookup.

    Argon2/bcrypt are intentionally non-deterministic (salted) and cannot be
    used for equality-based database lookups.  SHA-256 is the correct primitive
    for opaque bearer tokens: fast, deterministic, and collision-resistant.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


class AuthenticationService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        refresh_token_repo: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.refresh_token_repo = refresh_token_repo

    async def authenticate(self, username: str, password: str) -> User:
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError("Invalid username or password")

        if not user.is_active:
            raise InactiveUserError("User account is disabled or deleted")

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedError("Account is temporarily locked")

        if not verify_password(password, user.password_hash):
            attempts = user.failed_login_attempts + 1
            updates = {
                "failed_login_attempts": attempts,
                "last_failed_login": datetime.now(timezone.utc),
            }
            if attempts >= 5:
                updates["locked_until"] = datetime.now(timezone.utc) + timedelta(
                    minutes=15
                )
            await self.user_repo.update(user, updates)
            await self.session.commit()
            raise InvalidCredentialsError("Invalid username or password")

        updates = {
            "failed_login_attempts": 0,
            "last_failed_login": None,
            "last_login": datetime.now(timezone.utc),
        }
        await self.user_repo.update(user, updates)

        return user

    async def create_user(
        self, data: dict[str, Any], assign_default_roles: List[str] = []
    ) -> User:
        """Creates a new user. Restricted to Admins in production."""
        if "password" not in data:
            raise ValueError("Password is required")

        raw_password = data.pop("password")
        data["password_hash"] = get_password_hash(raw_password)

        user = await self.user_repo.create(data)

        for role_name in assign_default_roles:
            role = await self.role_repo.get_by_name(role_name)
            if role:
                await self.user_repo.assign_role(user, role)

        # The service layer owns the transaction boundary
        await self.session.commit()
        return user

    async def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """Generates a secure opaque refresh token and persists its SHA-256 hash."""
        token = secrets.token_hex(32)
        token_hash = _hash_refresh_token(token)

        expiry = datetime.now(timezone.utc) + timedelta(
            days=7
        )  # configurable via settings in the future

        await self.refresh_token_repo.create(
            {"user_id": user_id, "token_hash": token_hash, "expiry": expiry}
        )

        # Don't commit yet — caller commits atomically with access token issuance
        return token

    async def login(self, username: str, password: str) -> Tuple[str, str]:
        """Authenticates user and returns (access_token, refresh_token)."""
        user = await self.authenticate(username, password)

        roles = [r.name for r in await self.user_repo.list_roles(user.id)]
        access_token = create_access_token(user.id, user.username, roles)
        refresh_token = await self.create_refresh_token(user.id)

        await self.session.commit()
        return access_token, refresh_token

    async def refresh_session(self, raw_refresh_token: str) -> Tuple[str, str]:
        """Refresh token rotation: revoke old token, issue new pair.

        The user identity is resolved from the stored token record — the caller
        does NOT supply a user_id, avoiding the need for a JWT in the request.
        """
        token_hash = _hash_refresh_token(raw_refresh_token)
        token_record = await self.refresh_token_repo.get_by_hash(token_hash)
        if (
            not token_record
            or token_record.revoked
            or token_record.expiry < datetime.now(timezone.utc)
        ):
            raise UnauthorizedError("Invalid or expired refresh token")

        # user_id comes from the stored record — not from a JWT claim
        resolved_user_id = token_record.user_id

        # Revoke the old token
        await self.refresh_token_repo.revoke(token_record)

        # Generate new session pair
        user = await self.user_repo.get_by_id(resolved_user_id)
        if not user:
            raise NotFoundError("User not found")

        roles = [r.name for r in await self.user_repo.list_roles(user.id)]
        access_token = create_access_token(user.id, user.username, roles)
        new_refresh_token = await self.create_refresh_token(user.id)

        await self.session.commit()
        return access_token, new_refresh_token

    async def logout(self, user_id: uuid.UUID, raw_refresh_token: str) -> None:
        token_hash = _hash_refresh_token(raw_refresh_token)
        token_record = await self.refresh_token_repo.get_by_hash(token_hash)
        if token_record and token_record.user_id == user_id:
            await self.refresh_token_repo.revoke(token_record)
            await self.session.commit()

    async def change_password(
        self, user_id: uuid.UUID, old_password: str, new_password: str
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Invalid old password")

        new_hash = get_password_hash(new_password)
        await self.user_repo.update(user, {"password_hash": new_hash})

        # Optionally revoke all refresh tokens for security
        await self.refresh_token_repo.revoke_all(user_id)

        await self.session.commit()

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        role = await self.role_repo.get_by_name(role_name)
        if not role:
            raise NotFoundError("Role not found")

        await self.user_repo.assign_role(user, role)
        await self.session.commit()

    async def remove_role(self, user_id: uuid.UUID, role_name: str) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        role = await self.role_repo.get_by_name(role_name)
        if not role:
            raise NotFoundError("Role not found")

        await self.user_repo.remove_role(user, role)
        await self.session.commit()

    async def get_current_permissions(self, user_id: uuid.UUID) -> List[str]:
        roles = await self.user_repo.list_roles(user_id)
        permissions = set()
        for role in roles:
            role_perms = await self.role_repo.list_permissions(role.id)
            for p in role_perms:
                permissions.add(p.name)
        return list(permissions)

    async def lock_account(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.user_repo.update(
            user,
            {
                "is_active": False,
                "locked_until": datetime.now(timezone.utc)
                + timedelta(days=3650),  # Locked effectively indefinitely
            },
        )

        await self.refresh_token_repo.revoke_all(user_id)
        await self.session.commit()

    async def unlock_account(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.user_repo.update(
            user,
            {
                "is_active": True,
                "locked_until": None,
                "failed_login_attempts": 0,
                "last_failed_login": None,
            },
        )
        await self.session.commit()
