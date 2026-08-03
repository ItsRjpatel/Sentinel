import uuid
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.models import Alert

class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AlertRepository(db)

    async def list_alerts_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        endpoint_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Alert], int]:
        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            severity=severity,
            status=status,
            endpoint_id=endpoint_id,
            search=search,
        )

    async def get_summary_counts(self) -> Dict[str, int]:
        return await self.repo.get_summary_counts()

    async def get_alert(self, alert_id: uuid.UUID) -> Alert:
        alert = await self.repo.get_by_id(alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return alert

    async def acknowledge_alert(self, alert_id: uuid.UUID, analyst: str) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "acknowledged"
        if not alert.assigned_analyst:
            alert.assigned_analyst = analyst
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def resolve_alert(self, alert_id: uuid.UUID, resolution_notes: Optional[str] = None) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "resolved"
        if resolution_notes:
            alert.resolution_notes = resolution_notes
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def reopen_alert(self, alert_id: uuid.UUID) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "active"
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def assign_alert(self, alert_id: uuid.UUID, analyst: str) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.assigned_analyst = analyst
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def add_note(self, alert_id: uuid.UUID, author: str, note_text: str) -> Alert:
        alert = await self.get_alert(alert_id)
        existing_notes = list(alert.notes or [])
        new_note = {
            "author": author,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": note_text,
        }
        existing_notes.append(new_note)
        alert.notes = existing_notes
        await self.db.commit()
        await self.db.refresh(alert)
        return alert
