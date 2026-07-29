import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.dependencies import get_auth_service, get_current_user
from app.modules.auth.models import Role, User

# Mock service dependency
mock_auth_service = AsyncMock()


def override_get_auth_service():
    return mock_auth_service


# Return a fully valid User mock
def override_get_current_user():
    return User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@example.com",
        is_active=True,
        is_verified=True,
        roles=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


app.dependency_overrides[get_auth_service] = override_get_auth_service
app.dependency_overrides[get_current_user] = override_get_current_user

# Mock permissions so all tests pass the require_permission check
mock_auth_service.get_current_permissions.return_value = [
    "users.read",
    "users.create",
    "users.update",
    "users.delete",
    "roles.read",
    "roles.create",
    "roles.update",
    "roles.delete",
    "permissions.read",
]

client = TestClient(app)


def test_login_success():
    mock_auth_service.login.return_value = ("access123", "refresh123")
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"] == "access123"
    assert data["data"]["refresh_token"] == "refresh123"


def test_login_validation_error():
    response = client.post("/api/v1/auth/login", json={"username": "admin"})
    assert response.status_code == 422


def test_get_me_success():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "admin"


def test_create_user_success():
    mock_user = User(
        id=uuid.uuid4(),
        username="new_user",
        email="new@example.com",
        is_active=True,
        is_verified=False,
        roles=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.create_user.return_value = mock_user

    response = client.post(
        "/api/v1/users",
        json={
            "username": "new_user",
            "email": "new@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "new_user"


def test_list_users():
    mock_user = User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@example.com",
        is_active=True,
        is_verified=True,
        roles=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.user_repo.list.return_value = [mock_user]

    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1


def test_delete_user():
    mock_user = User(id=uuid.uuid4(), username="admin")
    mock_auth_service.user_repo.get_by_id.return_value = mock_user

    response = client.delete(f"/api/v1/users/{mock_user.id}")
    assert response.status_code == 204


def test_list_roles():
    mock_role = Role(
        id=uuid.uuid4(),
        name="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.role_repo.list.return_value = [mock_role]

    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"][0]["name"] == "admin"
