from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, get_current_user
from app.modules.auth.models import User
from app.modules.alerts.service import AlertService
from app.modules.alerts.schemas import (
    AlertResponse,
    PaginatedAlertsResponse,
    AlertSummaryData,
    AlertAssignRequest,
    AlertNoteRequest,
    AlertResolveRequest,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _to_alert_dto(a) -> AlertResponse:
    return AlertResponse(
        id=a.id,
        title=a.title,
        severity=a.severity,
        category=a.category or "Security Audit",
        description=a.description,
        endpoint_id=a.endpoint_id,
        endpoint_name=a.endpoint_name,
        status=a.status,
        assigned_analyst=a.assigned_analyst,
        resolution_notes=a.resolution_notes,
        notes=a.notes or [],
        created_at=a.created_at,
        updated_at=getattr(a, "updated_at", None),
    )


@router.get("/summary", response_model=SuccessResponse[AlertSummaryData])
async def get_alerts_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    counts = await service.get_summary_counts()
    return SuccessResponse(
        message="Alerts summary retrieved", data=AlertSummaryData(**counts)
    )


@router.get("", response_model=SuccessResponse[PaginatedAlertsResponse])
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    endpoint_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alerts, total = await service.list_alerts_paginated(
        page=page,
        page_size=page_size,
        severity=severity,
        status=status,
        endpoint_id=endpoint_id,
        search=search,
    )
    items = [_to_alert_dto(a) for a in alerts]
    return SuccessResponse(
        message="Alerts listed successfully",
        data=PaginatedAlertsResponse(
            items=items, total=total, page=page, size=page_size
        ),
    )


@router.get("/{alert_id}", response_model=SuccessResponse[AlertResponse])
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alert = await service.get_alert(alert_id)
    return SuccessResponse(message="Alert retrieved", data=_to_alert_dto(alert))


@router.patch("/{alert_id}/acknowledge", response_model=SuccessResponse[AlertResponse])
async def acknowledge_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alert = await service.acknowledge_alert(alert_id, analyst=current_user.username)
    return SuccessResponse(message="Alert acknowledged", data=_to_alert_dto(alert))


@router.patch("/{alert_id}/resolve", response_model=SuccessResponse[AlertResponse])
async def resolve_alert(
    alert_id: UUID,
    body: Optional[AlertResolveRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    notes = body.resolution_notes if body else None
    alert = await service.resolve_alert(alert_id, resolution_notes=notes)
    return SuccessResponse(message="Alert resolved", data=_to_alert_dto(alert))


@router.patch("/{alert_id}/reopen", response_model=SuccessResponse[AlertResponse])
async def reopen_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alert = await service.reopen_alert(alert_id)
    return SuccessResponse(message="Alert reopened", data=_to_alert_dto(alert))


@router.patch("/{alert_id}/assign", response_model=SuccessResponse[AlertResponse])
async def assign_alert(
    alert_id: UUID,
    body: AlertAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alert = await service.assign_alert(alert_id, analyst=body.analyst)
    return SuccessResponse(
        message="Alert assigned successfully", data=_to_alert_dto(alert)
    )


@router.post("/{alert_id}/notes", response_model=SuccessResponse[AlertResponse])
async def add_note(
    alert_id: UUID,
    body: AlertNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AlertService(db)
    alert = await service.add_note(
        alert_id, author=current_user.username, note_text=body.note
    )
    return SuccessResponse(message="Note added successfully", data=_to_alert_dto(alert))
