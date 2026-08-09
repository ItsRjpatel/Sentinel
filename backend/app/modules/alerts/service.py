from app.core.websocket.manager import connection_manager
from app.core.websocket.schema import WebSocketEvent
import uuid
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.models import Alert
from app.modules.alerts.models import Alert, AlertRule, EndpointAlertState
from sqlalchemy import select
from app.modules.endpoints.models import Endpoint
import logging

logger = logging.getLogger(__name__)

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

    async def delete_alert(self, alert_id: uuid.UUID) -> bool:
        success = await self.repo.delete(alert_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return success

    async def get_or_create_state(self, endpoint_id: uuid.UUID, alert_type: str) -> EndpointAlertState:
        stmt = select(EndpointAlertState).where(
            EndpointAlertState.endpoint_id == endpoint_id,
            EndpointAlertState.alert_type == alert_type
        ).with_for_update()
        res = await self.db.execute(stmt)
        state = res.scalar_one_or_none()
        if not state:
            state = EndpointAlertState(
                endpoint_id=endpoint_id,
                alert_type=alert_type,
                consecutive_trigger_samples=0,
                consecutive_resolve_samples=0
            )
            self.db.add(state)
        return state

    async def _handle_alert_state(
        self,
        endpoint: Endpoint,
        rule: AlertRule,
        state: EndpointAlertState,
        is_triggering: bool,
        is_resolving: bool
    ):
        active_alert_stmt = select(Alert).where(
            Alert.endpoint_id == endpoint.id,
            Alert.alert_type == rule.alert_type,
            Alert.status == "active"
        )
        res = await self.db.execute(active_alert_stmt)
        active_alert = res.scalar_one_or_none()

        if is_triggering:
            state.consecutive_trigger_samples += 1
            state.consecutive_resolve_samples = 0
            if state.consecutive_trigger_samples >= rule.trigger_duration_samples:
                if not active_alert:
                    new_alert = Alert(
                        alert_type=rule.alert_type,
                        title=f"{rule.category}: {rule.alert_type} on {endpoint.hostname}",
                        severity=rule.severity,
                        category=rule.category,
                        description=f"Triggered by {rule.alert_type} conditions.",
                        endpoint_id=endpoint.id,
                        endpoint_name=endpoint.hostname,
                        status="active"
                    )
                    self.db.add(new_alert)
                    await self.db.flush()
                    logger.info(f"Alert triggered: {rule.alert_type} for {endpoint.hostname}")
                    
                    from app.modules.alerts.schemas import AlertResponse
                    payload = AlertResponse(
                        id=new_alert.id, title=new_alert.title, severity=new_alert.severity,
                        category=new_alert.category, description=new_alert.description,
                        endpoint_id=new_alert.endpoint_id, endpoint_name=new_alert.endpoint_name,
                        status=new_alert.status, notes=[], created_at=datetime.now(timezone.utc)
                    ).model_dump(mode='json')
                    await connection_manager.broadcast(WebSocketEvent(event_type='alert_created', payload=payload))
                    
                    from app.modules.notifications.service import NotificationService
                    from app.modules.notifications.schemas import NotificationCreate
                    notif_svc = NotificationService(self.db)
                    await notif_svc.create_notification(NotificationCreate(
                        title=f"New Alert: {rule.alert_type}",
                        message=f"{rule.category} alert triggered on {endpoint.hostname}",
                        severity=rule.severity,
                        category="Alerts",
                        link=f"/endpoints/{endpoint.id}"
                    ))
        else:
            state.consecutive_trigger_samples = 0

        if is_resolving:
            state.consecutive_resolve_samples += 1
            if state.consecutive_resolve_samples >= rule.resolve_duration_samples:
                if active_alert:
                    active_alert.status = "resolved"
                    active_alert.resolution_notes = "Automatically resolved by telemetry."
                    await self.db.flush()
                    logger.info(f"Alert resolved: {rule.alert_type} for {endpoint.hostname}")
                    
                    await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(active_alert.id), "status": "resolved"}))

                    from app.modules.notifications.service import NotificationService
                    from app.modules.notifications.schemas import NotificationCreate
                    notif_svc = NotificationService(self.db)
                    await notif_svc.create_notification(NotificationCreate(
                        title=f"Alert Resolved: {rule.alert_type}",
                        message=f"{rule.category} alert resolved automatically on {endpoint.hostname}",
                        severity="low",
                        category="Alerts",
                        link=f"/endpoints/{endpoint.id}"
                    ))
        else:
            state.consecutive_resolve_samples = 0

        state.last_evaluated_at = datetime.now(timezone.utc)

    async def evaluate_telemetry(self, endpoint: Endpoint, metrics: Dict[str, Any], security: Optional[Dict[str, Any]]):
        rules_res = await self.db.execute(select(AlertRule).where(AlertRule.is_enabled == True))
        rules = rules_res.scalars().all()

        for rule in rules:
            state = await self.get_or_create_state(endpoint.id, rule.alert_type)
            is_triggering = False
            is_resolving = False

            if rule.alert_type == "high_cpu" and "cpu_usage_percent" in metrics:
                val = metrics["cpu_usage_percent"]
                if val >= rule.trigger_threshold: is_triggering = True
                if val <= rule.resolve_threshold: is_resolving = True

            elif rule.alert_type == "high_memory" and "memory_usage_percent" in metrics:
                val = metrics["memory_usage_percent"]
                if val >= rule.trigger_threshold: is_triggering = True
                if val <= rule.resolve_threshold: is_resolving = True

            elif rule.alert_type == "high_disk" and "disk_usage_percent" in metrics:
                val = metrics["disk_usage_percent"]
                if val >= rule.trigger_threshold: is_triggering = True
                if val <= rule.resolve_threshold: is_resolving = True

            elif rule.alert_type == "defender_disabled" and security is not None:
                is_disabled = not security.get("defender_enabled", True)
                if is_disabled:
                    is_triggering = True
                else:
                    is_resolving = True

            elif rule.alert_type == "real_time_protection_disabled" and security is not None:
                is_disabled = not security.get("real_time_protection_enabled", True)
                if is_disabled:
                    is_triggering = True
                else:
                    is_resolving = True

            elif rule.alert_type == "firewall_disabled" and security is not None:
                domain = security.get("firewall_domain_enabled", True)
                private = security.get("firewall_private_enabled", True)
                public = security.get("firewall_public_enabled", True)
                if not (domain and private and public):
                    is_triggering = True
                else:
                    is_resolving = True

            if is_triggering or is_resolving:
                await self._handle_alert_state(endpoint, rule, state, is_triggering, is_resolving)

        await self.db.commit()

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
        await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(alert.id), "status": alert.status, "assigned_analyst": alert.assigned_analyst}))
        return alert

    async def resolve_alert(self, alert_id: uuid.UUID, resolution_notes: Optional[str] = None) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "resolved"
        if resolution_notes:
            alert.resolution_notes = resolution_notes
        await self.db.commit()
        await self.db.refresh(alert)
        await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(alert.id), "status": alert.status, "resolution_notes": alert.resolution_notes}))
        return alert

    async def reopen_alert(self, alert_id: uuid.UUID) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "active"
        await self.db.commit()
        await self.db.refresh(alert)
        await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(alert.id), "status": alert.status}))
        return alert

    async def assign_alert(self, alert_id: uuid.UUID, analyst: str) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.assigned_analyst = analyst
        await self.db.commit()
        await self.db.refresh(alert)
        await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(alert.id), "assigned_analyst": alert.assigned_analyst}))
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
        await connection_manager.broadcast(WebSocketEvent(event_type='alert_updated', payload={"id": str(alert.id), "notes": alert.notes}))
        return alert
