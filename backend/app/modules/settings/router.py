from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, get_current_user
from app.modules.auth.models import User
from app.modules.settings.service import SettingService
from app.modules.settings.schemas import SettingItem, SettingUpdateRequest

router = APIRouter(prefix="/settings", tags=["settings"])

def _to_setting_dto(s) -> SettingItem:
    return SettingItem(
        id=s.id,
        key=s.key,
        category=s.category,
        value=s.value or {},
        description=s.description,
    )

@router.get("", response_model=SuccessResponse[List[SettingItem]])
async def list_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingService(db)
    settings = await service.list_settings()
    items = [_to_setting_dto(s) for s in settings]
    return SuccessResponse(message="System settings retrieved", data=items)

@router.put("/{key}", response_model=SuccessResponse[SettingItem])
async def update_setting(
    key: str,
    body: SettingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingService(db)
    setting = await service.update_setting(key, body.value)
    return SuccessResponse(message="Setting updated successfully", data=_to_setting_dto(setting))
