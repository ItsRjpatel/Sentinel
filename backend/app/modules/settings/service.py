from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.settings.repository import SettingRepository
from app.modules.settings.models import SystemSetting

class SettingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SettingRepository(db)

    async def list_settings(self) -> List[SystemSetting]:
        return await self.repo.get_all()

    async def update_setting(self, key: str, value: dict) -> SystemSetting:
        return await self.repo.update_value(key, value)
