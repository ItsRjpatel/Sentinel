import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import (
    AccountLockedError,
    InactiveUserError,
    PermissionDeniedError,
)
from app.modules.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_db,
    get_permission_repository,
    get_refresh_token_repository,
    get_role_repository,
    get_user_repository,
    require_permission,
)
from app.modules.auth.models import User
from app.modules.auth.repository import (
    PermissionRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)
from app.modules.auth.service import AuthenticationService


@pytest.mark.asyncio
async def test_get_db():
    async for session in get_db():
        assert session is not None
        break


def test_get_user_repository():
    mock_session = AsyncMock()
    repo = get_user_repository(session=mock_session)
    assert isinstance(repo, UserRepository)
    assert repo.session == mock_session


def test_get_role_repository():
    mock_session = AsyncMock()
    repo = get_role_repository(session=mock_session)
    assert isinstance(repo, RoleRepository)
    assert repo.session == mock_session


def test_get_permission_repository():
    mock_session = AsyncMock()
    repo = get_permission_repository(session=mock_session)
    assert isinstance(repo, PermissionRepository)
    assert repo.session == mock_session


def test_get_refresh_token_repository():
    mock_session = AsyncMock()
    repo = get_refresh_token_repository(session=mock_session)
    assert isinstance(repo, RefreshTokenRepository)
    assert repo.session == mock_session


def test_get_auth_service():
    mock_session = AsyncMock()
    user_repo = get_user_repository(session=mock_session)
    role_repo = get_role_repository(session=mock_session)
    permission_repo = get_permission_repository(session=mock_session)
    refresh_token_repo = get_refresh_token_repository(session=mock_session)

    service = get_auth_service(
        session=mock_session,
        user_repo=user_repo,
        role_repo=role_repo,
        permission_repo=permission_repo,
        refresh_token_repo=refresh_token_repo,
    )

    assert isinstance(service, AuthenticationService)


@pytest.mark.asyncio
@patch("app.modules.auth.dependencies.verify_access_token")
async def test_get_current_user_success(mock_verify_token):
    user_id = uuid.uuid4()
    mock_verify_token.return_value = {"sub": str(user_id)}

    mock_auth_service = AsyncMock()
    mock_user = User(id=user_id, is_active=True, locked_until=None)
    mock_auth_service.user_repo.get_by_id.return_value = mock_user

    user = await get_current_user("token", auth_service=mock_auth_service)
    assert user.id == user_id


@pytest.mark.asyncio
@patch("app.modules.auth.dependencies.verify_access_token")
async def test_get_current_user_inactive(mock_verify_token):
    user_id = uuid.uuid4()
    mock_verify_token.return_value = {"sub": str(user_id)}

    mock_auth_service = AsyncMock()
    mock_user = User(id=user_id, is_active=False, locked_until=None)
    mock_auth_service.user_repo.get_by_id.return_value = mock_user

    with pytest.raises(InactiveUserError):
        await get_current_user("token", auth_service=mock_auth_service)


@pytest.mark.asyncio
@patch("app.modules.auth.dependencies.verify_access_token")
async def test_get_current_user_locked(mock_verify_token):
    from datetime import datetime, timedelta, timezone

    user_id = uuid.uuid4()
    mock_verify_token.return_value = {"sub": str(user_id)}

    mock_auth_service = AsyncMock()
    mock_user = User(
        id=user_id,
        is_active=True,
        locked_until=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    mock_auth_service.user_repo.get_by_id.return_value = mock_user

    with pytest.raises(AccountLockedError):
        await get_current_user("token", auth_service=mock_auth_service)


@pytest.mark.asyncio
async def test_require_permission_success():
    dep_func = require_permission("users.read")
    mock_auth_service = AsyncMock()
    mock_auth_service.get_current_permissions.return_value = ["users.read"]
    mock_user = User(id=uuid.uuid4())

    user = await dep_func(current_user=mock_user, auth_service=mock_auth_service)
    assert user == mock_user


@pytest.mark.asyncio
async def test_require_permission_denied():
    dep_func = require_permission("users.delete")
    mock_auth_service = AsyncMock()
    mock_auth_service.get_current_permissions.return_value = ["users.read"]
    mock_user = User(id=uuid.uuid4())

    with pytest.raises(PermissionDeniedError):
        await dep_func(current_user=mock_user, auth_service=mock_auth_service)
