from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    NotificationPreferenceSchema
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    return await service.list_notifications(current_user.id, unread_only)

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    return await service.create_notification(data)

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    await service.mark_as_read(notification_id)
    return {"message": "Notification marked as read"}

@router.post("/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    await service.mark_all_read(current_user.id)
    return {"message": "All notifications marked as read"}

@router.get("/preferences", response_model=NotificationPreferenceSchema)
async def get_notification_preferences(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    return await service.get_preferences(current_user.id)

@router.post("/preferences", response_model=NotificationPreferenceSchema)
async def save_notification_preferences(
    data: NotificationPreferenceSchema,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = NotificationService(db)
    return await service.save_preferences(current_user.id, data)
