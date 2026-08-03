import uuid
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.audit.repository import AuditRepository
from app.modules.audit.models import AuditLog

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuditRepository(db)

    async def list_audit_logs_paginated(
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
        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            search=search,
            severity=severity,
            module=module,
            actor=actor,
            endpoint_id=endpoint_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_summary(self) -> Dict[str, int]:
        return await self.repo.get_summary_counts()

    async def get_audit_log(self, log_id: uuid.UUID) -> AuditLog:
        log = await self.repo.get_by_id(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log entry not found")
        return log
