from typing import AsyncGenerator, Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AccountLockedError,
    InactiveUserError,
    InvalidTokenError,
    PermissionDeniedError,
)
from app.core.security import verify_access_token
from app.db.session import async_session_maker
from app.modules.auth.models import User
from app.modules.auth.repository import (
    PermissionRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)
from app.modules.auth.service import AuthenticationService

# OAuth2 scheme configures Swagger UI to send tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing a request-scoped database session."""
    async with async_session_maker() as session:
        yield session


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency for UserRepository."""
    return UserRepository(session)


def get_role_repository(session: AsyncSession = Depends(get_db)) -> RoleRepository:
    """Dependency for RoleRepository."""
    return RoleRepository(session)


def get_permission_repository(
    session: AsyncSession = Depends(get_db),
) -> PermissionRepository:
    """Dependency for PermissionRepository."""
    return PermissionRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db),
) -> RefreshTokenRepository:
    """Dependency for RefreshTokenRepository."""
    return RefreshTokenRepository(session)


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    permission_repo: PermissionRepository = Depends(get_permission_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthenticationService:
    """Dependency for AuthenticationService. Injects Repositories and Session."""
    return AuthenticationService(
        session=session,
        user_repo=user_repo,
        role_repo=role_repo,
        permission_repo=permission_repo,
        refresh_token_repo=refresh_token_repo,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> User:
    """
    Validates the JWT access token and resolves the authenticated User.
    Rejects inactive and locked users.
    """
    # Verify signature and expiration
    payload = verify_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidTokenError("Token missing 'sub' claim.")

    import uuid

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise InvalidTokenError("Invalid 'sub' claim format.")

    user = await auth_service.user_repo.get_by_id(user_id)
    if not user:
        raise InvalidTokenError("User not found.")

    if not user.is_active:
        raise InactiveUserError("User account is disabled or deleted.")

    from datetime import datetime, timezone

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise AccountLockedError("User account is temporarily locked.")

    return user


def require_permission(permission_name: str) -> Callable[..., User]:
    """
    Dependency factory to enforce permission-based authorization.
    Avoids duplicate aggregation logic by reusing auth_service.get_current_permissions.
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user),
        auth_service: AuthenticationService = Depends(get_auth_service),
    ) -> User:
        permissions = await auth_service.get_current_permissions(current_user.id)
        if permission_name not in permissions:
            raise PermissionDeniedError(
                f"Missing required permission: {permission_name}"
            )
        return current_user

    return permission_checker
