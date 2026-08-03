from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, get_current_user, require_permission
from app.modules.auth.models import User
from app.modules.users.service import UserService
from app.modules.users.schemas import (
    UserItemResponse,
    PaginatedUsersResponse,
    UsersSummary,
    UserCreateRequest,
    UserUpdateRequest,
    PasswordResetRequest,
    UserRolesAssignRequest,
)

router = APIRouter(prefix="/users", tags=["users"])

def _to_user_dto(u) -> UserItemResponse:
    now_utc = datetime.now(timezone.utc)
    is_locked = bool(u.locked_until and u.locked_until > now_utc)
    role_names = [r.name for r in (u.roles or [])]
    if not role_names:
        role_names = ["Analyst"]

    return UserItemResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        first_name=u.first_name,
        last_name=u.last_name,
        phone=u.phone,
        is_active=u.is_active,
        is_verified=u.is_verified,
        is_locked=is_locked,
        last_login=u.last_login,
        created_at=u.created_at,
        roles=role_names,
    )

@router.get("/summary", response_model=SuccessResponse[UsersSummary])
async def get_users_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    counts = await service.get_summary()
    return SuccessResponse(message="User summary retrieved", data=UsersSummary(**counts))

@router.get("", response_model=SuccessResponse[PaginatedUsersResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users.read")),
):
    service = UserService(db)
    users, total = await service.list_users_paginated(
        page=page, page_size=page_size, search=search, role=role, status=status
    )
    items = [_to_user_dto(u) for u in users]
    return SuccessResponse(
        message="Users listed successfully",
        data=PaginatedUsersResponse(items=items, total=total, page=page, size=page_size),
    )

@router.get("/{id}", response_model=SuccessResponse[UserItemResponse])
async def get_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.get_user(id)
    return SuccessResponse(message="User retrieved", data=_to_user_dto(user))

@router.post("", response_model=SuccessResponse[UserItemResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.create_user(body)
    return SuccessResponse(message="User created successfully", data=_to_user_dto(user))

@router.put("/{id}", response_model=SuccessResponse[UserItemResponse])
async def update_user(
    id: UUID,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.update_user(id, body)
    return SuccessResponse(message="User updated successfully", data=_to_user_dto(user))

@router.patch("/{id}/enable", response_model=SuccessResponse[UserItemResponse])
async def enable_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.enable_user(id)
    return SuccessResponse(message="User enabled", data=_to_user_dto(user))

@router.patch("/{id}/disable", response_model=SuccessResponse[UserItemResponse])
async def disable_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.disable_user(id)
    return SuccessResponse(message="User disabled", data=_to_user_dto(user))

@router.patch("/{id}/unlock", response_model=SuccessResponse[UserItemResponse])
async def unlock_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.unlock_user(id)
    return SuccessResponse(message="User unlocked", data=_to_user_dto(user))

@router.post("/{id}/reset-password", response_model=SuccessResponse[UserItemResponse])
async def reset_password(
    id: UUID,
    body: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.reset_password(id, body.new_password)
    return SuccessResponse(message="Password reset successfully", data=_to_user_dto(user))

@router.delete("/{id}", response_model=SuccessResponse[dict])
async def delete_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    await service.delete_user(id)
    return SuccessResponse(message="User deleted successfully", data={"id": str(id)})
