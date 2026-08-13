import uuid
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog
from datetime import datetime, timezone


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, log_id: uuid.UUID) -> Optional[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        severity: Optional[str] = None,
        module: Optional[str] = None,
        actor: Optional[str] = None,
        endpoint_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> Tuple[List[AuditLog], int]:
        stmt = select(AuditLog)

        if severity and severity.upper() != "ALL":
            stmt = stmt.where(func.upper(AuditLog.severity) == severity.upper())
        if module and module.upper() != "ALL":
            stmt = stmt.where(func.upper(AuditLog.module) == module.upper())
        if actor and actor.upper() != "ALL":
            stmt = stmt.where(func.lower(AuditLog.actor) == actor.lower())
        if endpoint_id:
            stmt = stmt.where(AuditLog.endpoint_id == endpoint_id)
        if status and status.upper() != "ALL":
            stmt = stmt.where(func.upper(AuditLog.status) == status.upper())

        if start_date:
            stmt = stmt.where(AuditLog.timestamp >= start_date)
        if end_date:
            stmt = stmt.where(AuditLog.timestamp <= end_date)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    AuditLog.action.ilike(pattern),
                    AuditLog.module.ilike(pattern),
                    AuditLog.actor.ilike(pattern),
                    AuditLog.endpoint_hostname.ilike(pattern),
                    AuditLog.resource.ilike(pattern),
                    AuditLog.correlation_id.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar() or 0

        # Ordering
        order_col = getattr(AuditLog, sort_by, AuditLog.timestamp)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(order_col.asc())
        else:
            stmt = stmt.order_by(order_col.desc())

        # Offset & Limit
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        res = await self.db.execute(stmt)
        logs = list(res.scalars().all())
        return logs, total

    async def get_summary_counts(self) -> Dict[str, int]:
        stmt = select(AuditLog.severity, AuditLog.status, AuditLog.timestamp)
        res = await self.db.execute(select(AuditLog))
        logs = list(res.scalars().all())

        now_utc = datetime.now(timezone.utc)

        counts = {
            "total": len(logs),
            "critical": 0,
            "warning": 0,
            "information": 0,
            "success": 0,
            "failed": 0,
            "today": 0,
        }

        for l in logs:
            sev_upper = (l.severity or "").upper()
            stat_upper = (l.status or "").upper()

            if sev_upper == "CRITICAL":
                counts["critical"] += 1
            elif sev_upper == "WARNING":
                counts["warning"] += 1
            elif sev_upper in ["INFO", "INFORMATION"]:
                counts["information"] += 1

            if stat_upper == "SUCCESS":
                counts["success"] += 1
            elif stat_upper in ["FAILED", "DENIED", "ERROR"]:
                counts["failed"] += 1

            if l.timestamp and l.timestamp.date() == now_utc.date():
                counts["today"] += 1

        return counts
