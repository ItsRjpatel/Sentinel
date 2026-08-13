import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    JSON,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base, BaseModelMixin


class ScheduledJob(Base, BaseModelMixin):
    __tablename__ = "scheduled_jobs"

    name = Column(String(255), nullable=False, index=True)
    job_type = Column(
        String(50), nullable=False
    )  # INVENTORY, COMMAND, POLICY_REFRESH, HEARTBEAT_CHECK, CLEANUP
    schedule_type = Column(
        String(50), nullable=False, default="RECURRING"
    )  # RECURRING or ONE_TIME
    cron_expression = Column(String(100), nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    last_run_at = Column(DateTime, nullable=True)
    status = Column(
        String(50), nullable=False, default="ACTIVE"
    )  # ACTIVE, PAUSED, COMPLETED, EXPIRED
    payload = Column(JSON, nullable=True)
    retry_count = Column(Integer, nullable=False, default=3)

    executions = relationship(
        "JobExecutionHistory", back_populates="job", cascade="all, delete-orphan"
    )


class JobExecutionHistory(Base, BaseModelMixin):
    __tablename__ = "job_execution_history"

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, RUNNING
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    job = relationship("ScheduledJob", back_populates="executions")
