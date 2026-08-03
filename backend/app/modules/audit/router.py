from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, get_current_user
from app.modules.auth.models import User
from app.modules.audit.service import AuditService
from app.modules.audit.schemas import (
    AuditLogItem,
    PaginatedAuditResponse,
    AuditSummary,
)

router = APIRouter(prefix="/audit", tags=["audit"])

def _to_audit_dto(l) -> AuditLogItem:
    return AuditLogItem(
        id=l.id,
        timestamp=l.timestamp,
        actor=l.actor,
        actor_type=l.actor_type,
        endpoint_id=l.endpoint_id,
        endpoint_hostname=l.endpoint_hostname,
        action=l.action,
        module=l.module,
        resource=l.resource,
        severity=l.severity,
        ip_address=l.ip_address,
        user_agent=l.user_agent,
        status=l.status,
        details=l.details or {},
        correlation_id=l.correlation_id,
    )

@router.get("/summary", response_model=SuccessResponse[AuditSummary])
async def get_audit_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    counts = await service.get_summary()
    return SuccessResponse(message="Audit log summary retrieved", data=AuditSummary(**counts))

@router.get("", response_model=SuccessResponse[PaginatedAuditResponse])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    endpoint_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    logs, total = await service.list_audit_logs_paginated(
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
    items = [_to_audit_dto(l) for l in logs]
    return SuccessResponse(
        message="Audit logs listed successfully",
        data=PaginatedAuditResponse(items=items, total=total, page=page, size=page_size),
    )

@router.get("/{id}", response_model=SuccessResponse[AuditLogItem])
async def get_audit_log_details(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    log = await service.get_audit_log(id)
    return SuccessResponse(message="Audit log retrieved", data=_to_audit_dto(log))
