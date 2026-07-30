from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.modules.commands.schemas import CommandCreate, CommandResponse, CommandQueueResponse
from app.modules.commands.service import CommandService
from app.modules.commands.enums import CommandStatus

router = APIRouter(prefix="/commands", tags=["commands"])
endpoint_router = APIRouter(prefix="/endpoints", tags=["commands"])

@router.post("", response_model=CommandQueueResponse, status_code=status.HTTP_201_CREATED)
def queue_command(
    command_in: CommandCreate,
    db: Session = Depends(get_db)
):
    service = CommandService(db)
    command = service.queue_command(command_in)
    return CommandQueueResponse(
        command_id=command.id,
        status=command.status,
        message="Command queued successfully."
    )

@router.get("/{command_id}", response_model=CommandResponse)
def get_command(
    command_id: UUID,
    db: Session = Depends(get_db)
):
    service = CommandService(db)
    return service.get_command(command_id)

@router.patch("/{command_id}/cancel", response_model=CommandResponse)
def cancel_command(
    command_id: UUID,
    db: Session = Depends(get_db)
):
    service = CommandService(db)
    return service.cancel_command(command_id)

@endpoint_router.get("/{endpoint_id}/commands", response_model=List[CommandResponse])
def get_endpoint_commands(
    endpoint_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = CommandService(db)
    return service.get_endpoint_commands(endpoint_id, skip=skip, limit=limit)
