from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.settings.models import SystemSetting


class SettingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[SystemSetting]:
        stmt = select(SystemSetting).order_by(SystemSetting.key.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_value(self, key: str, value: dict) -> SystemSetting:
        setting = await self.get_by_key(key)
        if not setting:
            setting = SystemSetting(key=key, value=value)
            self.db.add(setting)
        else:
            setting.value = value
        await self.db.commit()
        await self.db.refresh(setting)
        return setting
