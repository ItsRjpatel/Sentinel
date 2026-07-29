import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.core.security import get_password_hash
from app.modules.auth.exceptions import InvalidCredentialsError, UnauthorizedError
from app.modules.auth.models import RefreshToken, Role, User
from app.modules.auth.service import AuthenticationService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session: AsyncMock) -> AuthenticationService:
    from app.modules.auth.repository import (
        PermissionRepository,
        RefreshTokenRepository,
        RoleRepository,
        UserRepository,
    )

    user_repo = UserRepository(mock_session)
    role_repo = RoleRepository(mock_session)
    permission_repo = PermissionRepository(mock_session)
    refresh_token_repo = RefreshTokenRepository(mock_session)

    return AuthenticationService(
        session=mock_session,
        user_repo=user_repo,
        role_repo=role_repo,
        permission_repo=permission_repo,
        refresh_token_repo=refresh_token_repo,
    )


@pytest.mark.asyncio
async def test_authenticate_success(auth_service: AuthenticationService) -> None:
    user_id = uuid.uuid4()
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    mock_user = User(
        id=user_id,
        username="admin",
        password_hash=hashed,
        is_active=True,
        failed_login_attempts=0,
    )

    auth_service.user_repo.get_by_username = AsyncMock(return_value=mock_user)  # type: ignore

    user = await auth_service.authenticate("admin", password)
    assert user.id == user_id


@pytest.mark.asyncio
async def test_authenticate_invalid_user(auth_service: AuthenticationService) -> None:
    auth_service.user_repo.get_by_username = AsyncMock(return_value=None)  # type: ignore

    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate("admin", "password")


@pytest.mark.asyncio
async def test_authenticate_invalid_password(
    auth_service: AuthenticationService,
) -> None:
    user_id = uuid.uuid4()
    hashed = get_password_hash("DifferentPassword")
    mock_user = User(
        id=user_id,
        username="admin",
        password_hash=hashed,
        is_active=True,
        failed_login_attempts=0,
    )

    auth_service.user_repo.get_by_username = AsyncMock(return_value=mock_user)  # type: ignore

    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate("admin", "WrongPassword")


@pytest.mark.asyncio
async def test_create_user(auth_service: AuthenticationService) -> None:
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, username="newuser")
    auth_service.user_repo.create = AsyncMock(return_value=mock_user)  # type: ignore
    auth_service.role_repo.get_by_name = AsyncMock(return_value=None)  # type: ignore

    user = await auth_service.create_user({"username": "newuser", "password": "secure"})
    assert user.id == user_id
    auth_service.session.commit.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
@patch("app.modules.auth.service.create_access_token")
async def test_login(
    mock_create_token: AsyncMock, auth_service: AuthenticationService
) -> None:
    user_id = uuid.uuid4()
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    mock_user = User(
        id=user_id,
        username="admin",
        password_hash=hashed,
        is_active=True,
        failed_login_attempts=0,
    )

    auth_service.user_repo.get_by_username = AsyncMock(return_value=mock_user)  # type: ignore
    auth_service.user_repo.list_roles = AsyncMock(return_value=[Role(name="admin")])  # type: ignore
    auth_service.refresh_token_repo.create = AsyncMock()  # type: ignore
    mock_create_token.return_value = "mock.jwt.token"

    access, refresh = await auth_service.login("admin", password)

    assert access == "mock.jwt.token"
    assert refresh is not None
    auth_service.session.commit.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
@patch("app.modules.auth.service.create_access_token")
async def test_refresh_session_success(
    mock_create_token: AsyncMock, auth_service: AuthenticationService
) -> None:
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, username="admin", is_active=True)
    token_record = RefreshToken(
        user_id=user_id,
        token_hash="hash",
        revoked=False,
        expiry=datetime.now(timezone.utc),
    )
    # Make token valid
    token_record.expiry = (
        datetime.now(timezone.utc) + datetime.timedelta(days=1)
        if hasattr(datetime, "timedelta")
        else datetime.fromtimestamp(
            datetime.now(timezone.utc).timestamp() + 86400, timezone.utc
        )
    )

    auth_service.refresh_token_repo.get_by_hash = AsyncMock(return_value=token_record)  # type: ignore
    auth_service.refresh_token_repo.revoke = AsyncMock()  # type: ignore
    auth_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)  # type: ignore
    auth_service.user_repo.list_roles = AsyncMock(return_value=[])  # type: ignore
    auth_service.refresh_token_repo.create = AsyncMock()  # type: ignore
    mock_create_token.return_value = "new.jwt.token"

    access, new_refresh = await auth_service.refresh_session("raw_token")

    assert access == "new.jwt.token"
    auth_service.refresh_token_repo.revoke.assert_awaited_once_with(token_record)
    auth_service.session.commit.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
async def test_refresh_session_revoked(auth_service: AuthenticationService) -> None:
    user_id = uuid.uuid4()
    token_record = RefreshToken(
        user_id=user_id,
        token_hash="hash",
        revoked=True,
        expiry=datetime.now(timezone.utc),
    )
    auth_service.refresh_token_repo.get_by_hash = AsyncMock(return_value=token_record)  # type: ignore

    with pytest.raises(UnauthorizedError):
        await auth_service.refresh_session("raw_token")
