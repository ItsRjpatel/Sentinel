from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime


class UserItemResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_locked: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    roles: List[str] = []


class PaginatedUsersResponse(BaseModel):
    items: List[UserItemResponse]
    total: int
    page: int
    size: int


class UsersSummary(BaseModel):
    total: int
    online: int
    disabled: int
    locked: int
    administrators: int
    analysts: int
    agents: int
    guests: int


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    roles: List[str] = ["Analyst"]


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class PasswordResetRequest(BaseModel):
    new_password: str


class UserRolesAssignRequest(BaseModel):
    roles: List[str]
