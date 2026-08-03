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
    severity: Mapped[str] = mapped_column(String(50), nullable=False)  # critical, high, medium, low, informational
    category: Mapped[str] = mapped_column(String(100), default="Security Audit", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    endpoint_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=True)
    endpoint_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, acknowledged, resolved
    assigned_analyst: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
