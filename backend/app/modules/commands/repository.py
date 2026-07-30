from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.modules.commands.models import Command
from app.modules.commands.enums import CommandStatus

def get_utc_now():
    return datetime.now(timezone.utc)

class CommandRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, command: Command) -> Command:
        self.session.add(command)
        self.session.commit()
        self.session.refresh(command)
        return command

    def get_by_id(self, command_id: UUID) -> Optional[Command]:
        return self.session.query(Command).filter(Command.id == command_id).first()

    def get_pending_for_endpoint(self, endpoint_id: UUID, command_type: str = None) -> List[Command]:
        query = self.session.query(Command).filter(
            Command.endpoint_id == endpoint_id,
            Command.status == CommandStatus.PENDING
        )
        if command_type:
            query = query.filter(Command.command_type == command_type)
        return query.order_by(Command.created_at.asc()).all()

    def mark_sent(self, command: Command) -> Command:
        command.status = CommandStatus.SENT
        self.session.commit()
        self.session.refresh(command)
        return command

    def mark_running(self, command: Command) -> Command:
        command.status = CommandStatus.RUNNING
        command.started_at = get_utc_now()
        self.session.commit()
        self.session.refresh(command)
        return command

    def mark_success(self, command: Command, result: dict = None) -> Command:
        command.status = CommandStatus.SUCCESS
        command.completed_at = get_utc_now()
        if result:
            command.result = result
        self.session.commit()
        self.session.refresh(command)
        return command

    def mark_failed(self, command: Command, error_message: str = None) -> Command:
        command.status = CommandStatus.FAILED
        command.completed_at = get_utc_now()
        if error_message:
            command.error_message = error_message
        self.session.commit()
        self.session.refresh(command)
        return command

    def mark_timeout(self, command: Command) -> Command:
        command.status = CommandStatus.TIMEOUT
        command.completed_at = get_utc_now()
        self.session.commit()
        self.session.refresh(command)
        return command
        
    def mark_cancelled(self, command: Command) -> Command:
        command.status = CommandStatus.CANCELLED
        command.completed_at = get_utc_now()
        self.session.commit()
        self.session.refresh(command)
        return command

    def list_by_endpoint(self, endpoint_id: UUID, skip: int = 0, limit: int = 100) -> List[Command]:
        return self.session.query(Command)\
            .filter(Command.endpoint_id == endpoint_id)\
            .order_by(Command.created_at.desc())\
            .offset(skip).limit(limit).all()

    def list_recent(self, skip: int = 0, limit: int = 100) -> List[Command]:
        return self.session.query(Command)\
            .order_by(Command.created_at.desc())\
            .offset(skip).limit(limit).all()
