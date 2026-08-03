import uuid
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.alerts.models import Alert
from datetime import datetime, timezone

class AlertRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, alert_id: uuid.UUID) -> Optional[Alert]:
        stmt = select(Alert).where(Alert.id == alert_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        endpoint_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Alert], int]:
        stmt = select(Alert)

        if severity and severity.upper() != "ALL":
            stmt = stmt.where(func.lower(Alert.severity) == severity.lower())
        if status and status.upper() != "ALL":
            stmt = stmt.where(func.lower(Alert.status) == status.lower())
        if endpoint_id:
            stmt = stmt.where(Alert.endpoint_id == endpoint_id)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Alert.title.ilike(search_pattern),
                    Alert.description.ilike(search_pattern),
                    Alert.endpoint_name.ilike(search_pattern),
                    Alert.category.ilike(search_pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar() or 0

        # Pagination & Order
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Alert.created_at.desc()).offset(offset).limit(page_size)

        res = await self.db.execute(stmt)
        alerts = list(res.scalars().all())
        return alerts, total

    async def get_summary_counts(self) -> Dict[str, int]:
        stmt = select(Alert.severity, Alert.status, func.count(Alert.id)).group_by(Alert.severity, Alert.status)
        res = await self.db.execute(stmt)
        rows = res.fetchall()

        counts = {
            "total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0,
            "active": 0,
            "acknowledged": 0,
            "resolved": 0,
        }

        for sev, stat, cnt in rows:
            counts["total"] += cnt
            sev_lower = (sev or "").lower()
            stat_lower = (stat or "").lower()

            if sev_lower in counts:
                counts[sev_lower] += cnt
            elif sev_lower == "info":
                counts["informational"] += cnt

            if stat_lower in counts:
                counts[stat_lower] += cnt

        return counts
