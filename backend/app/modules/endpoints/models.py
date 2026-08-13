import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import BaseModelMixin
from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Endpoint(Base, BaseModelMixin):
    """Database model for registered Windows Agent endpoints."""

    __tablename__ = "endpoints"

    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, nullable=False
    )
    identity_version: Mapped[int] = mapped_column(default=1, nullable=False)
    identity_anomaly: Mapped[bool] = mapped_column(default=False, nullable=False)
    os_version: Mapped[str] = mapped_column(String(255), nullable=False)
    hardware_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    mac_addresses: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ip_addresses: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="healthy", nullable=False)
    config_version: Mapped[str] = mapped_column(
        String(50), default="1.0.0", nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
