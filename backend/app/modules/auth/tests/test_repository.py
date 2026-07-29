import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError as SAIntegrityError

from app.modules.auth.exceptions import DuplicateEntryError, IntegrityError, NotFoundError
from app.modules.auth.models import Permission, RefreshToken, Role, User
from app.modules.auth.repository import (
    PermissionRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_user_repo_create(mock_session: AsyncMock) -> None:
    repo = UserRepository(mock_session)
    data = {"username": "testuser", "email": "test@example.com", "password_hash": "hash"}
    
    user = await repo.create(data)
    
    assert user.username == "testuser"
    mock_session.add.assert_called_once_with(user)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_repo_create_duplicate(mock_session: AsyncMock) -> None:
    repo = UserRepository(mock_session)
    data = {"username": "testuser", "email": "test@example.com", "password_hash": "hash"}
    
    # Simulate integrity error
    mock_session.flush.side_effect = SAIntegrityError("statement", "params", Exception("unique constraint"))
    
    with pytest.raises(DuplicateEntryError):
        await repo.create(data)


@pytest.mark.asyncio
async def test_user_repo_get_by_id(mock_session: AsyncMock) -> None:
    repo = UserRepository(mock_session)
    user_id = uuid.uuid4()
    
    mock_result = MagicMock()
    mock_user = User(id=user_id, username="testuser")
    mock_result.scalars().first.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_id(user_id)
    
    assert result == mock_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_repo_soft_delete(mock_session: AsyncMock) -> None:
    repo = UserRepository(mock_session)
    user = User(id=uuid.uuid4(), username="testuser", is_active=True)
    
    deleted_user = await repo.soft_delete(user)
    
    assert deleted_user.is_active is False
    assert deleted_user.deleted_at is not None
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_repo_assign_role(mock_session: AsyncMock) -> None:
    repo = UserRepository(mock_session)
    user = User(id=uuid.uuid4(), username="testuser")
    role = Role(id=uuid.uuid4(), name="admin")
    
    # Mock relations list
    user.roles = []
    
    updated_user = await repo.assign_role(user, role)
    
    assert role in updated_user.roles
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_repo_create(mock_session: AsyncMock) -> None:
    repo = RoleRepository(mock_session)
    data = {"name": "admin", "description": "Admin role"}
    
    role = await repo.create(data)
    
    assert role.name == "admin"
    mock_session.add.assert_called_once_with(role)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_role_repo_assign_permission(mock_session: AsyncMock) -> None:
    repo = RoleRepository(mock_session)
    role = Role(id=uuid.uuid4(), name="admin")
    permission = Permission(id=uuid.uuid4(), name="users.read")
    role.permissions = []
    
    updated_role = await repo.assign_permission(role, permission)
    
    assert permission in updated_role.permissions
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_permission_repo_get_by_name(mock_session: AsyncMock) -> None:
    repo = PermissionRepository(mock_session)
    
    mock_result = MagicMock()
    mock_permission = Permission(id=uuid.uuid4(), name="users.read")
    mock_result.scalars().first.return_value = mock_permission
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_name("users.read")
    
    assert result == mock_permission


@pytest.mark.asyncio
async def test_refresh_token_repo_revoke(mock_session: AsyncMock) -> None:
    repo = RefreshTokenRepository(mock_session)
    token = RefreshToken(id=uuid.uuid4(), token_hash="hash", expiry=datetime.now(timezone.utc), user_id=uuid.uuid4())
    
    revoked_token = await repo.revoke(token)
    
    assert revoked_token.revoked is True
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_token_repo_cleanup_expired(mock_session: AsyncMock) -> None:
    repo = RefreshTokenRepository(mock_session)
    
    await repo.cleanup_expired()
    
    mock_session.execute.assert_awaited_once()
    mock_session.flush.assert_awaited_once()
