import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import BaseModelMixin
from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base, BaseModelMixin):
    """Database model for enterprise system audit logs."""

    __tablename__ = "audit_logs"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    actor: Mapped[str] = mapped_column(String(255), default="admin", nullable=False)
    actor_type: Mapped[str] = mapped_column(
        String(50), default="USER", nullable=False
    )  # USER, AGENT, SYSTEM
    endpoint_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=True
    )
    endpoint_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    severity: Mapped[str] = mapped_column(
        String(50), default="INFORMATION", nullable=False
    )  # CRITICAL, WARNING, INFORMATION, SUCCESS, FAILED
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="SUCCESS", nullable=False
    )  # SUCCESS, FAILED, DENIED
    details: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
