import os
from unittest.mock import AsyncMock, patch

import pytest

from scripts.bootstrap import (
    DEFAULT_PERMISSIONS,
    DEFAULT_ROLES,
    bootstrap_permissions,
    bootstrap_roles,
)
from scripts.bootstrap_admin import create_super_admin


@pytest.mark.asyncio
async def test_bootstrap_permissions_fresh():
    mock_permission_repo = AsyncMock()
    mock_session = AsyncMock()

    # Simulate fresh database: get_by_name returns None
    mock_permission_repo.get_by_name.return_value = None

    await bootstrap_permissions(mock_permission_repo, mock_session)

    assert mock_permission_repo.create.call_count == len(DEFAULT_PERMISSIONS)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_bootstrap_permissions_idempotent():
    mock_permission_repo = AsyncMock()
    mock_session = AsyncMock()

    # Simulate populated database: get_by_name returns an existing permission
    mock_permission_repo.get_by_name.return_value = True

    await bootstrap_permissions(mock_permission_repo, mock_session)

    # Should not create any permissions
    mock_permission_repo.create.assert_not_called()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_bootstrap_roles_fresh():
    mock_role_repo = AsyncMock()
    mock_permission_repo = AsyncMock()
    mock_session = AsyncMock()

    # Fresh DB
    mock_role_repo.get_by_name.return_value = None

    # Mock returning all permissions for Super Administrator role mapping
    mock_permission_repo.list.return_value = ["perm1", "perm2"]

    # Mock create returning a Role object
    mock_role = AsyncMock()
    mock_role_repo.create.return_value = mock_role

    await bootstrap_roles(mock_role_repo, mock_permission_repo, mock_session)

    assert mock_role_repo.create.call_count == len(DEFAULT_ROLES)
    # The Super Admin role assignment should happen for the 2 mocked perms
    assert mock_role_repo.assign_permission.call_count == 2
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_bootstrap_roles_idempotent():
    mock_role_repo = AsyncMock()
    mock_permission_repo = AsyncMock()
    mock_session = AsyncMock()

    # Populated DB
    mock_role_repo.get_by_name.return_value = True

    await bootstrap_roles(mock_role_repo, mock_permission_repo, mock_session)

    mock_role_repo.create.assert_not_called()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch.dict(os.environ, {"BOOTSTRAP_ADMIN_PASSWORD": "TestPassword123!"})
@patch("scripts.bootstrap_admin.UserRepository")
@patch("scripts.bootstrap_admin.RoleRepository")
@patch("scripts.bootstrap_admin.get_password_hash")
async def test_create_super_admin_fresh(mock_hash, MockRoleRepo, MockUserRepo):
    mock_session = AsyncMock()

    mock_user_repo_instance = MockUserRepo.return_value
    mock_role_repo_instance = MockRoleRepo.return_value

    # Fresh DB
    created_user_mock = AsyncMock()
    mock_user_repo_instance.get_by_username = AsyncMock(
        side_effect=[None, created_user_mock]
    )
    mock_user_repo_instance.create = AsyncMock(return_value=created_user_mock)
    mock_user_repo_instance.assign_role = AsyncMock()

    mock_hash.return_value = "hashed_pw"

    mock_super_admin_role = AsyncMock()
    mock_role_repo_instance.get_by_name = AsyncMock(return_value=mock_super_admin_role)

    await create_super_admin(mock_session)

    # Asserts
    mock_user_repo_instance.create.assert_awaited_once()
    assert mock_user_repo_instance.create.call_args[0][0]["username"] == "admin"
    assert (
        mock_user_repo_instance.create.call_args[0][0]["password_hash"] == "hashed_pw"
    )

    mock_user_repo_instance.assign_role.assert_awaited_once_with(
        mock_user_repo_instance.create.return_value, mock_super_admin_role
    )
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch.dict(os.environ, {"BOOTSTRAP_ADMIN_PASSWORD": "TestPassword123!"})
@patch("scripts.bootstrap_admin.UserRepository")
@patch("scripts.bootstrap_admin.RoleRepository")
async def test_create_super_admin_idempotent(MockRoleRepo, MockUserRepo):
    mock_session = AsyncMock()

    mock_user_repo_instance = MockUserRepo.return_value

    # Populated DB
    mock_user_repo_instance.get_by_username = AsyncMock(return_value=True)
    mock_user_repo_instance.create = AsyncMock()

    await create_super_admin(mock_session)

    mock_user_repo_instance.create.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
@patch.dict(os.environ, {}, clear=True)
async def test_create_super_admin_no_password():
    mock_session = AsyncMock()
    await create_super_admin(mock_session)
    mock_session.commit.assert_not_called()
