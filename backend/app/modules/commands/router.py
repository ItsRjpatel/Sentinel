from fastapi import APIRouter, Depends, Query, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import math

from app.common.schemas import SuccessResponse
from app.db.session import get_db
from app.core.security import verify_access_token
from app.modules.auth.dependencies import get_current_user, oauth2_scheme
from app.modules.auth.models import User
from app.modules.commands.schemas import (
    CommandCreate,
    CommandResponse,
    CommandQueueResponse,
    CommandSummary,
    BulkCommandCreate,
    BulkCommandResponse,
    PaginatedCommandResponse,
    CommandResultRequest,
)
from app.modules.commands.service import CommandService

router = APIRouter(prefix="/commands", tags=["commands"])
endpoint_router = APIRouter(prefix="/endpoints", tags=["commands"])


def _to_response_dto(c) -> CommandResponse:
    ep_hostname = None
    ep_type = None
    try:
        # Check __dict__ to avoid triggering async lazy load on unloaded relationship
        if "endpoint" in c.__dict__ and c.endpoint:
            ep_hostname = c.endpoint.hostname
            ep_type = getattr(c.endpoint, "os_version", "Windows Workstation")
    except Exception:
        pass

    return CommandResponse(
        id=c.id,
        endpoint_id=c.endpoint_id,
        endpoint_hostname=ep_hostname,
        endpoint_type=ep_type,
        command_type=c.command_type,
        status=c.status,
        payload=c.payload,
        created_by=c.created_by,
        created_at=c.created_at,
        started_at=c.started_at,
        completed_at=c.completed_at,
        result=c.result,
        error_message=c.error_message,
        retry_count=c.retry_count,
        expires_at=c.expires_at,
        scheduled_at=c.scheduled_at,
        recurring=c.recurring,
        timezone=c.timezone,
    )


@router.get("/summary", response_model=SuccessResponse[CommandSummary])
async def get_commands_summary(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = CommandService(db)
    counts = await service.get_summary_counts()
    summary = CommandSummary(**counts)
    return SuccessResponse(message="Command summary retrieved", data=summary)


@router.get("", response_model=SuccessResponse[PaginatedCommandResponse])
async def list_commands(
    status: Optional[str] = Query(
        None,
        description="Filter by status (PENDING, RUNNING, SUCCESS, FAILED, TIMEOUT, CANCELLED, SCHEDULED)",
    ),
    command_type: Optional[str] = Query(None, description="Filter by command type"),
    endpoint_id: Optional[UUID] = Query(None, description="Filter by endpoint ID"),
    search: Optional[str] = Query(
        None, description="Search by command type, creator, or hostname"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    commands, total = await service.list_commands_paginated(
        status_filter=status,
        command_type=command_type,
        endpoint_id=endpoint_id,
        search=search,
        page=page,
        page_size=page_size,
    )

    items = [_to_response_dto(c) for c in commands]
    paginated = PaginatedCommandResponse(
        items=items, total=total, page=page, size=page_size
    )
    return SuccessResponse(message="Commands listed successfully", data=paginated)


@router.post(
    "", response_model=CommandQueueResponse, status_code=status.HTTP_201_CREATED
)
async def queue_command(
    command_in: CommandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    command_in.created_by = current_user.username
    command = await service.queue_command(command_in)
    return CommandQueueResponse(
        command_id=command.id,
        status=command.status,
        message="Command queued successfully.",
    )


@router.post(
    "/bulk",
    response_model=SuccessResponse[BulkCommandResponse],
    status_code=status.HTTP_201_CREATED,
)
async def queue_bulk_commands(
    bulk_in: BulkCommandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    res = await service.queue_bulk_commands(bulk_in, created_by=current_user.username)
    return SuccessResponse(
        message=f"Queued {res.queued_count} commands successfully.", data=res
    )


@router.post("/{command_id}/retry", response_model=SuccessResponse[CommandResponse])
async def retry_command(
    command_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    new_cmd = await service.retry_command(command_id, created_by=current_user.username)
    dto = _to_response_dto(new_cmd)
    return SuccessResponse(message="Command retry queued successfully.", data=dto)


@router.get(
    "/poll",
    response_model=CommandResponse,
    responses={204: {"description": "No pending commands"}},
)
async def poll_command(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )

    agent_id_str = payload.get("sub")
    if not agent_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identifier.",
        )

    try:
        endpoint_id = UUID(agent_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject UUID format.",
        )

    service = CommandService(db)
    command = await service.poll_command(endpoint_id)
    if not command:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return _to_response_dto(command)


@router.get("/{command_id}", response_model=CommandResponse)
async def get_command(
    command_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    cmd = await service.get_command(command_id)
    return _to_response_dto(cmd)


@router.post("/{command_id}/result", response_model=CommandResponse)
async def upload_command_result(
    command_id: UUID,
    result_in: CommandResultRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )

    service = CommandService(db)
    cmd = await service.update_command_result(
        command_id=command_id,
        success=result_in.success,
        result=result_in.result,
        error_message=result_in.error,
    )
    return _to_response_dto(cmd)


@router.patch("/{command_id}/cancel", response_model=CommandResponse)
async def cancel_command(
    command_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    cmd = await service.cancel_command(command_id)
    return _to_response_dto(cmd)


@endpoint_router.get("/{endpoint_id}/commands", response_model=List[CommandResponse])
async def get_endpoint_commands(
    endpoint_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    commands = await service.get_endpoint_commands(endpoint_id, skip=skip, limit=limit)
    return [_to_response_dto(c) for c in commands]
