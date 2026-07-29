from unittest.mock import AsyncMock

import pytest

from app.modules.auth.dependencies import (
    get_auth_service,
    get_db,
    get_permission_repository,
    get_refresh_token_repository,
    get_role_repository,
    get_user_repository,
)
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
        # Validate that it yields something session-like (in this context we just check it doesn't fail)
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

    # We simulate fastapi dependency injection manually here to prove wiring
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
    assert service.session == mock_session
    assert service.user_repo == user_repo
    assert service.role_repo == role_repo
    assert service.permission_repo == permission_repo
    assert service.refresh_token_repo == refresh_token_repo

    # Verify they all share the exact same session instance
    assert service.user_repo.session is service.session
    assert service.role_repo.session is service.session
    assert service.permission_repo.session is service.session
    assert service.refresh_token_repo.session is service.session
