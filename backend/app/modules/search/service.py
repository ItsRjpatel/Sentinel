from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.endpoints.models import Endpoint
from app.modules.auth.models import User
from app.modules.commands.models import Command
from app.modules.alerts.models import Alert
from app.modules.policies.models import Policy
from app.modules.audit.models import AuditLog


class GlobalSearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_all(self, query_str: str) -> Dict[str, List[Dict[str, Any]]]:
        if not query_str or len(query_str.strip()) < 2:
            return {
                "endpoints": [],
                "users": [],
                "commands": [],
                "alerts": [],
                "policies": [],
                "audit": [],
            }

        term = f"%{query_str}%"

        # 1. Search Endpoints
        ep_res = await self.session.execute(
            select(Endpoint)
            .where((Endpoint.hostname.ilike(term)) | (Endpoint.ip_address.ilike(term)))
            .limit(5)
        )
        endpoints = [
            {
                "id": e.id,
                "title": e.hostname or e.id,
                "subtitle": f"IP: {e.ip_address} • {e.os_version}",
                "type": "endpoint",
                "link": f"/endpoints/{e.id}",
            }
            for e in ep_res.scalars().all()
        ]

        # 2. Search Users
        usr_res = await self.session.execute(
            select(User)
            .where((User.username.ilike(term)) | (User.email.ilike(term)))
            .limit(5)
        )
        users = [
            {
                "id": u.id,
                "title": u.username,
                "subtitle": u.email,
                "type": "user",
                "link": "/users",
            }
            for u in usr_res.scalars().all()
        ]

        # 3. Search Commands
        cmd_res = await self.session.execute(
            select(Command)
            .where((Command.command_type.ilike(term)) | (Command.id.ilike(term)))
            .limit(5)
        )
        commands = [
            {
                "id": c.id,
                "title": c.command_type,
                "subtitle": f"Status: {c.status} • ID: {c.id[:8]}",
                "type": "command",
                "link": "/commands",
            }
            for c in cmd_res.scalars().all()
        ]

        # 4. Search Alerts
        alt_res = await self.session.execute(
            select(Alert)
            .where((Alert.title.ilike(term)) | (Alert.description.ilike(term)))
            .limit(5)
        )
        alerts = [
            {
                "id": a.id,
                "title": a.title,
                "subtitle": f"Severity: {a.severity} • Status: {a.status}",
                "type": "alert",
                "link": "/alerts",
            }
            for a in alt_res.scalars().all()
        ]

        # 5. Search Policies
        pol_res = await self.session.execute(
            select(Policy)
            .where((Policy.name.ilike(term)) | (Policy.category.ilike(term)))
            .limit(5)
        )
        policies = [
            {
                "id": p.id,
                "title": p.name,
                "subtitle": f"Category: {p.category} • v{p.version}",
                "type": "policy",
                "link": f"/policies/{p.id}",
            }
            for p in pol_res.scalars().all()
        ]

        # 6. Search Audit Logs
        aud_res = await self.session.execute(
            select(AuditLog)
            .where((AuditLog.action.ilike(term)) | (AuditLog.username.ilike(term)))
            .limit(5)
        )
        audit = [
            {
                "id": a.id,
                "title": a.action,
                "subtitle": f"User: {a.username or 'system'} • {a.created_at}",
                "type": "audit",
                "link": "/audit",
            }
            for a in aud_res.scalars().all()
        ]

        return {
            "endpoints": endpoints,
            "users": users,
            "commands": commands,
            "alerts": alerts,
            "policies": policies,
            "audit": audit,
        }
