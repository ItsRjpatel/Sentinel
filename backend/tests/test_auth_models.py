import pytest
from pydantic import ValidationError
from sqlalchemy.orm import class_mapper

from app.modules.auth.models import Permission, RefreshToken, Role, User
from app.modules.auth.schemas import CreateUser


def test_user_model_attributes():
    """Verify that User model has all required attributes and relationships."""
    mapper = class_mapper(User)
    
    # Check attributes
    assert "id" in mapper.columns
    assert "username" in mapper.columns
    assert "email" in mapper.columns
    assert "password_hash" in mapper.columns
    assert "is_active" in mapper.columns
    assert "deleted_at" in mapper.columns
    
    # Check relationships
    relationships = [r.key for r in mapper.relationships]
    assert "roles" in relationships
    assert "refresh_tokens" in relationships


def test_role_model_attributes():
    """Verify that Role model has all required attributes and relationships."""
    mapper = class_mapper(Role)
    
    assert "name" in mapper.columns
    relationships = [r.key for r in mapper.relationships]
    assert "users" in relationships
    assert "permissions" in relationships


def test_permission_model_attributes():
    """Verify that Permission model has all required attributes and relationships."""
    mapper = class_mapper(Permission)
    
    assert "name" in mapper.columns
    relationships = [r.key for r in mapper.relationships]
    assert "roles" in relationships


def test_refresh_token_model_attributes():
    """Verify that RefreshToken model has all required attributes and relationships."""
    mapper = class_mapper(RefreshToken)
    
    assert "token_hash" in mapper.columns
    assert "expiry" in mapper.columns
    relationships = [r.key for r in mapper.relationships]
    assert "user" in relationships


def test_create_user_schema_valid():
    """Test valid CreateUser schema."""
    user = CreateUser(
        username="admin",
        email="admin@example.com",
        password="securepassword123",
    )
    assert user.username == "admin"
    assert user.email == "admin@example.com"


def test_create_user_schema_invalid_email():
    """Test invalid email in CreateUser schema."""
    with pytest.raises(ValidationError):
        CreateUser(
            username="admin",
            email="invalid-email",
            password="securepassword123",
        )


def test_create_user_schema_invalid_password():
    """Test password length constraint."""
    with pytest.raises(ValidationError):
        CreateUser(
            username="admin",
            email="admin@example.com",
            password="short",
        )
