import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.modules.commands.enums import CommandStatus, CommandType


def get_utc_now():
    return datetime.now(timezone.utc)


class Command(Base):
    __tablename__ = "commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
    )
    command_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=CommandStatus.PENDING)
    payload = Column(JSONB, nullable=True)
    created_by = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    result = Column(JSONB, nullable=True)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    recurring = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    endpoint = relationship("Endpoint", backref="commands")

    __table_args__ = (
        Index("ix_commands_endpoint_id", "endpoint_id"),
        Index("ix_commands_status", "status"),
        Index("ix_commands_command_type", "command_type"),
        Index("ix_commands_created_at", "created_at"),
    )
