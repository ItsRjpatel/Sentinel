import pytest
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from httpx import AsyncClient

from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.modules.auth.models import User, Role, Permission, UserRole, RefreshToken
from app.modules.auth.dependencies import get_current_user
from scripts.bootstrap import bootstrap_permissions, bootstrap_roles
from scripts.bootstrap_admin import create_super_admin


@pytest.fixture
async def setup_test_roles_perms(db_session):
    """Seed base permissions and roles for integration tests using scripts."""
    # Run the bootstrap functions inside test transaction
    from app.modules.auth.repository import PermissionRepository, RoleRepository
    perm_repo = PermissionRepository(db_session)
    role_repo = RoleRepository(db_session)
    
    await bootstrap_permissions(perm_repo, db_session)
    await bootstrap_roles(role_repo, perm_repo, db_session)
    
    # Commit changes to the test savepoint
    await db_session.commit()


@pytest.mark.asyncio
async def test_login_success(client, db_session, setup_test_roles_perms):
    """Verify that a temporary user can login successfully with correct credentials."""
    username = "temp_user_success"
    email = "temp_success@example.com"
    password = "SecurePassword123!"
    
    # Create temp user
    pw_hash = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        password_hash=pw_hash,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test Login
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert "access_token" in res_data["data"]
    assert "refresh_token" in res_data["data"]


@pytest.mark.asyncio
async def test_login_invalid_password(client, db_session, setup_test_roles_perms):
    """Verify that login fails with an incorrect password."""
    username = "temp_user_wrong_pw"
    email = "temp_wrong_pw@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "WrongPassword!"},
    )
    assert resp.status_code == 400
    res_data = resp.json()
    assert res_data["success"] is False
    assert res_data["error_code"] == "AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_invalid_username(client, setup_test_roles_perms):
    """Verify that login fails with a non-existent username."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "non_existent_user_123", "password": "SomePassword123!"},
    )
    assert resp.status_code == 400
    res_data = resp.json()
    assert res_data["success"] is False
    assert res_data["error_code"] == "AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_inactive_account(client, db_session, setup_test_roles_perms):
    """Verify that an inactive user is rejected with 401 status."""
    username = "temp_inactive_user"
    email = "temp_inactive@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    # The application handler maps InactiveUserError to 401 AUTH_INACTIVE_USER
    assert resp.status_code == 401
    res_data = resp.json()
    assert res_data["success"] is False
    assert res_data["error_code"] == "AUTH_INACTIVE_USER"


@pytest.mark.asyncio
async def test_login_locked_account(client, db_session, setup_test_roles_perms):
    """Verify that an account is locked after 5 failed login attempts and rejects login."""
    username = "temp_locked_user"
    email = "temp_locked@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Try 5 failed logins
    for _ in range(5):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "WrongPassword!"},
        )
        assert resp.status_code == 400
        
    # The 6th attempt with CORRECT password must fail due to locked account status
    resp_correct = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp_correct.status_code == 401
    res_data = resp_correct.json()
    assert res_data["success"] is False
    assert res_data["error_code"] == "AUTH_ACCOUNT_LOCKED"


@pytest.mark.asyncio
async def test_jwt_claims_and_signature(client, db_session, setup_test_roles_perms):
    """Verify JWT token payload structure and signature verification."""
    username = "temp_jwt_user"
    email = "temp_jwt@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    
    # Decode and check claims
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == str(user.id)
    assert decoded["username"] == username
    assert "roles" in decoded
    assert decoded["token_type"] == "access"
    
    # Verify decoding with WRONG secret raises exception
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "WrongSecretKeyValue", algorithms=[settings.ALGORITHM])


@pytest.mark.asyncio
async def test_jwt_expired_token(client):
    """Verify that an expired token is rejected with 401."""
    expired_token = create_access_token(
        subject=uuid.uuid4(),
        username="temp_user",
        roles=[],
        expires_delta=timedelta(seconds=-10),
    )
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    res_data = resp.json()
    assert res_data["success"] is False
    assert "expire" in res_data["message"].lower() or "expired" in res_data["message"].lower()


@pytest.mark.asyncio
async def test_jwt_malformed_token(client):
    """Verify that a malformed token is rejected with 401."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer malformed.jwt.token"},
    )
    assert resp.status_code == 401
    res_data = resp.json()
    assert res_data["success"] is False
    assert res_data["error_code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_jwt_missing_token(client):
    """Verify that missing token returns 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_protected_vs_anonymous(client):
    """Verify protected endpoints reject anonymous calls, and public endpoints allow them."""
    # Protected
    resp_protected = await client.get("/api/v1/auth/me")
    assert resp_protected.status_code == 401
    
    # Public (Validation error expected, but not unauthorized error)
    resp_public = await client.post("/api/v1/auth/login", json={})
    assert resp_public.status_code == 422


@pytest.mark.asyncio
async def test_auth_permission_enforcement(client, db_session, setup_test_roles_perms):
    """Verify that role and permission restrictions are enforced correctly (403)."""
    username = "temp_viewer_user"
    email = "temp_viewer@example.com"
    password = "SecurePassword123!"
    
    # Create viewer role with no permissions or viewer-only roles
    viewer_role = await db_session.execute(
        text("SELECT * FROM roles WHERE name = 'Viewer'")
    )
    viewer_role_row = viewer_role.first()
    assert viewer_role_row is not None
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    
    # Assign Viewer role
    user_role_link = UserRole(user_id=user.id, role_id=viewer_role_row.id)
    db_session.add(user_role_link)
    await db_session.commit()
    
    # Login as viewer
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    
    # Attempt to list users (requires 'users.read' permission, which Viewer doesn't have)
    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["success"] is False
    assert resp.json()["error_code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_user_me(client, db_session, setup_test_roles_perms):
    """Verify /me profile retrieval."""
    username = "temp_profile_user"
    email = "temp_profile@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    token = login_resp.json()["data"]["access_token"]
    
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["data"]["username"] == username
    assert res_data["data"]["email"] == email


@pytest.mark.asyncio
async def test_user_refresh_rotation(client, db_session, setup_test_roles_perms):
    """Verify token rotation on session refresh."""
    username = "temp_rotation_user"
    email = "temp_rotation@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]
    
    # Perform refresh
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    ref_data = refresh_resp.json()
    assert ref_data["success"] is True
    assert "access_token" in ref_data["data"]
    assert "refresh_token" in ref_data["data"]
    
    new_refresh = ref_data["data"]["refresh_token"]
    
    # Try refreshing AGAIN with the rotated (revoked) token -> should fail
    resp_revoked = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp_revoked.status_code == 401


@pytest.mark.asyncio
async def test_user_logout(client, db_session, setup_test_roles_perms):
    """Verify session revocation upon logout."""
    username = "temp_logout_user"
    email = "temp_logout@example.com"
    password = "SecurePassword123!"
    
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    access_token = login_resp.json()["data"]["access_token"]
    refresh_token = login_resp.json()["data"]["refresh_token"]
    
    # Logout
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200
    
    # Assert token refresh fails after logout
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_db_unique_constraints(db_session):
    """Verify that database unique constraints are enforced properly."""
    u1 = User(username="unique_user", email="u1@example.com", password_hash="hash")
    db_session.add(u1)
    await db_session.commit()
    
    # Duplicate username
    u2 = User(username="unique_user", email="u2@example.com", password_hash="hash")
    db_session.add(u2)
    with pytest.raises(Exception):
        await db_session.commit()
    await db_session.rollback()
    
    # Duplicate email
    u3 = User(username="unique_user_diff", email="u1@example.com", password_hash="hash")
    db_session.add(u3)
    with pytest.raises(Exception):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_db_cascade_deletes(db_session, setup_test_roles_perms):
    """Verify foreign key ondelete cascade deletions."""
    user = User(username="cascade_user", email="cascade@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()
    
    # Create refresh token
    token = RefreshToken(token_hash="somehashvalue", expiry=datetime.now(timezone.utc), user_id=user.id)
    db_session.add(token)
    
    # Create user role links
    role_res = await db_session.execute(text("SELECT id FROM roles WHERE name = 'Viewer'"))
    role_id = role_res.scalar()
    user_role = UserRole(user_id=user.id, role_id=role_id)
    db_session.add(user_role)
    await db_session.commit()
    
    # Verify items exist
    r_token = await db_session.execute(text("SELECT COUNT(*) FROM refresh_tokens WHERE user_id = :uid"), {"uid": user.id})
    assert r_token.scalar() == 1
    
    r_role = await db_session.execute(text("SELECT COUNT(*) FROM user_roles WHERE user_id = :uid"), {"uid": user.id})
    assert r_role.scalar() == 1
    
    # Delete User
    await db_session.delete(user)
    await db_session.commit()
    
    # Verify cascaded rows are gone
    r_token_after = await db_session.execute(text("SELECT COUNT(*) FROM refresh_tokens WHERE user_id = :uid"), {"uid": user.id})
    assert r_token_after.scalar() == 0
    
    r_role_after = await db_session.execute(text("SELECT COUNT(*) FROM user_roles WHERE user_id = :uid"), {"uid": user.id})
    assert r_role_after.scalar() == 0


@pytest.mark.asyncio
async def test_db_migration_state(db_session):
    """Verify that Alembic migrations version row is present and synchronized."""
    res = await db_session.execute(text("SELECT COUNT(*) FROM alembic_version"))
    count = res.scalar()
    assert count == 1, "Expected exactly 1 migration row in alembic_version table"


@pytest.mark.asyncio
async def test_bootstrap_idempotency_real_db(db_session):
    """Verify that running bootstrap multiple times does not duplicate roles or permissions."""
    from app.modules.auth.repository import PermissionRepository, RoleRepository
    perm_repo = PermissionRepository(db_session)
    role_repo = RoleRepository(db_session)
    
    # First bootstrap
    await bootstrap_permissions(perm_repo, db_session)
    await bootstrap_roles(role_repo, perm_repo, db_session)
    await db_session.commit()
    
    # Get current counts
    perm_count_1 = (await db_session.execute(text("SELECT COUNT(*) FROM permissions"))).scalar()
    role_count_1 = (await db_session.execute(text("SELECT COUNT(*) FROM roles"))).scalar()
    
    # Second bootstrap run
    await bootstrap_permissions(perm_repo, db_session)
    await bootstrap_roles(role_repo, perm_repo, db_session)
    await db_session.commit()
    
    perm_count_2 = (await db_session.execute(text("SELECT COUNT(*) FROM permissions"))).scalar()
    role_count_2 = (await db_session.execute(text("SELECT COUNT(*) FROM roles"))).scalar()
    
    assert perm_count_1 == perm_count_2
    assert role_count_1 == role_count_2


@pytest.mark.asyncio
async def test_bootstrap_non_destructive_real_db(db_session, setup_test_roles_perms):
    """Verify bootstrap execution never overwrites or resets administrator accounts."""
    # Create the administrator first
    await create_super_admin(db_session)
    
    admin_res = await db_session.execute(text("SELECT password_hash FROM users WHERE username = 'admin'"))
    original_pw_hash = admin_res.scalar()
    assert original_pw_hash is not None
    
    # Modify the administrator password hash manually to simulate change
    modified_hash = "manual_modified_hash_value"
    await db_session.execute(
        text("UPDATE users SET password_hash = :hash WHERE username = 'admin'"),
        {"hash": modified_hash}
    )
    await db_session.commit()
    
    # Run the bootstrap create_super_admin again
    await create_super_admin(db_session)
    
    # Assert password hash is NOT overwritten
    admin_after = await db_session.execute(text("SELECT password_hash FROM users WHERE username = 'admin'"))
    assert admin_after.scalar() == modified_hash, "Admin credentials must not be reset by bootstrap seeding"
