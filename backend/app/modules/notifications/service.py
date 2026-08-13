from app.core.websocket.manager import connection_manager
from app.core.websocket.schema import WebSocketEvent
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.models import Notification, NotificationPreference
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationPreferenceSchema,
)
from app.modules.notifications.channels import NotificationChannelSender


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NotificationRepository(session)

    async def create_notification(self, data: NotificationCreate) -> Notification:
        notif = Notification(
            title=data.title,
            message=data.message,
            severity=data.severity,
            category=data.category,
            user_id=data.user_id,
            link=data.link,
            details=data.details,
        )
        created = await self.repo.create(notif)

        # Dispatch via configured channel abstractions
        if data.user_id:
            pref = await self.repo.get_preferences(data.user_id)
            if pref:
                if pref.email_enabled and pref.email_address:
                    await NotificationChannelSender.send_email(
                        pref.email_address, data.title, data.message
                    )
                if pref.webhook_enabled and pref.webhook_url:
                    await NotificationChannelSender.send_webhook(
                        pref.webhook_url, {"title": data.title, "message": data.message}
                    )
                if pref.slack_enabled and pref.slack_webhook_url:
                    await NotificationChannelSender.send_slack(
                        pref.slack_webhook_url, data.title, data.message
                    )
                if pref.teams_enabled and pref.teams_webhook_url:
                    await NotificationChannelSender.send_teams(
                        pref.teams_webhook_url, data.title, data.message
                    )

        from app.modules.notifications.schemas import NotificationResponse

        payload = NotificationResponse.model_validate(created).model_dump(mode="json")
        await connection_manager.broadcast(
            WebSocketEvent(event_type="notification_created", payload=payload)
        )
        return created

    async def list_notifications(
        self, user_id: Optional[str] = None, unread_only: bool = False
    ) -> List[Notification]:
        return await self.repo.list_notifications(user_id, unread_only)

    async def mark_as_read(self, notification_id: str) -> bool:
        res = await self.repo.mark_as_read(notification_id)
        if res:
            await connection_manager.broadcast(
                WebSocketEvent(
                    event_type="notification_read", payload={"id": notification_id}
                )
            )
        return res

    async def mark_all_read(self, user_id: Optional[str] = None) -> bool:
        res = await self.repo.mark_all_read(user_id)
        if res:
            await connection_manager.broadcast(
                WebSocketEvent(
                    event_type="notification_all_read", payload={"user_id": user_id}
                )
            )
        return res

    async def get_preferences(self, user_id: str) -> NotificationPreferenceSchema:
        pref = await self.repo.get_preferences(user_id)
        if not pref:
            return NotificationPreferenceSchema()
        return NotificationPreferenceSchema.model_validate(pref)

    async def save_preferences(
        self, user_id: str, data: NotificationPreferenceSchema
    ) -> NotificationPreferenceSchema:
        pref = NotificationPreference(
            user_id=user_id,
            email_enabled=data.email_enabled,
            email_address=data.email_address,
            webhook_enabled=data.webhook_enabled,
            webhook_url=data.webhook_url,
            slack_enabled=data.slack_enabled,
            slack_webhook_url=data.slack_webhook_url,
            teams_enabled=data.teams_enabled,
            teams_webhook_url=data.teams_webhook_url,
            min_severity=data.min_severity,
        )
        saved = await self.repo.save_preferences(pref)
        return NotificationPreferenceSchema.model_validate(saved)
