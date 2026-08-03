from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notifications.models import Notification, NotificationPreference

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notif: Notification) -> Notification:
        self.session.add(notif)
        await self.session.commit()
        await self.session.refresh(notif)
        return notif

    async def list_notifications(self, user_id: Optional[str] = None, unread_only: bool = False) -> List[Notification]:
        query = select(Notification)
        if user_id:
            query = query.where((Notification.user_id == user_id) | (Notification.user_id == None))
        if unread_only:
            query = query.where(Notification.is_read == False)
        result = await self.session.execute(query.order_by(Notification.created_at.desc()))
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: str) -> bool:
        await self.session.execute(
            update(Notification).where(Notification.id == notification_id).values(is_read=True)
        )
        await self.session.commit()
        return True

    async def mark_all_read(self, user_id: Optional[str] = None) -> bool:
        query = update(Notification).values(is_read=True)
        if user_id:
            query = query.where((Notification.user_id == user_id) | (Notification.user_id == None))
        await self.session.execute(query)
        await self.session.commit()
        return True

    async def get_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        result = await self.session.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalars().first()

    async def save_preferences(self, pref: NotificationPreference) -> NotificationPreference:
        existing = await self.get_preferences(pref.user_id)
        if existing:
            existing.email_enabled = pref.email_enabled
            existing.email_address = pref.email_address
            existing.webhook_enabled = pref.webhook_enabled
            existing.webhook_url = pref.webhook_url
            existing.slack_enabled = pref.slack_enabled
            existing.slack_webhook_url = pref.slack_webhook_url
            existing.teams_enabled = pref.teams_enabled
            existing.teams_webhook_url = pref.teams_webhook_url
            existing.min_severity = pref.min_severity
            await self.session.commit()
            return existing
        else:
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)
            return pref
