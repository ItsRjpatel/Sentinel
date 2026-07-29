from datetime import datetime

from pydantic import EmailStr, Field

from app.common.schemas import BaseResponseSchema, CoreModel


class PermissionResponse(BaseResponseSchema):
    """Schema for returning a Permission."""

    name: str = Field(
        ..., description="Unique name of the permission, e.g., users.read"
    )
    description: str | None = Field(None, description="Description of the permission")


class RoleResponse(BaseResponseSchema):
    """Schema for returning a Role."""

    name: str = Field(..., description="Unique name of the role")
    description: str | None = Field(None, description="Description of the role")
    permissions: list[PermissionResponse] = []


class UserResponse(BaseResponseSchema):
    """Schema for returning a User."""

    username: str
    email: EmailStr
    first_name: str | None
    last_name: str | None
    phone: str | None
    is_verified: bool
    last_login: datetime | None
    roles: list[RoleResponse] = []


class CreateUser(CoreModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    roles: list[str] = []
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class UpdateUser(CoreModel):
    """Schema for updating an existing user."""

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class CreateRole(CoreModel):
    name: str = Field(..., min_length=3)
    description: str | None = None


class UpdateRole(CoreModel):
    description: str | None = None


class LoginRequest(CoreModel):
    """Schema for authenticating a user."""

    username: str = Field(...)
    password: str = Field(...)


class RefreshRequest(CoreModel):
    refresh_token: str = Field(...)


class LogoutRequest(CoreModel):
    refresh_token: str = Field(...)


class ChangePasswordRequest(CoreModel):
    old_password: str = Field(...)
    new_password: str = Field(..., min_length=12)


class TokenPair(CoreModel):
    """Schema for token pairs returned upon login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
