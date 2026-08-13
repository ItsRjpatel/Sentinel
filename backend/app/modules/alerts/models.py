import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import BaseModelMixin
from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base, BaseModelMixin):
    """Database model for security alerts."""

    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    alert_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="custom"
    )
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # critical, high, medium, low, informational
    category: Mapped[str] = mapped_column(
        String(100), default="Security Audit", nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    endpoint_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=True
    )
    endpoint_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # active, acknowledged, resolved
    assigned_analyst: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


from sqlalchemy import Float, Integer, Boolean


class AlertRule(Base, BaseModelMixin):
    """Configuration rules for alert thresholds."""

    __tablename__ = "alert_rules"

    alert_type: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    trigger_threshold: Mapped[float] = mapped_column(
        Float, nullable=False, default=90.0
    )
    trigger_duration_samples: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    resolve_threshold: Mapped[float] = mapped_column(
        Float, nullable=False, default=80.0
    )
    resolve_duration_samples: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="high")
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Performance"
    )


class EndpointAlertState(Base, BaseModelMixin):
    """Tracks consecutive samples and evaluation state per endpoint and alert_type without polluting the Endpoint table."""

    __tablename__ = "endpoint_alert_states"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    consecutive_trigger_samples: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    consecutive_resolve_samples: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
