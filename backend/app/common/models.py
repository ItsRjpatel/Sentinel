import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, mapped_column


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


@declarative_mixin
class UUIDMixin:
    """Provides a UUID primary key for models."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )


@declarative_mixin
class TimestampMixin:
    """Provides created_at and updated_at timestamps for models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


@declarative_mixin
class AuditMixin:
    """Provides created_by and updated_by fields for models."""

    @declared_attr
    def created_by(cls) -> Mapped[uuid.UUID | None]:
        return mapped_column(
            Uuid(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )

    @declared_attr
    def updated_by(cls) -> Mapped[uuid.UUID | None]:
        return mapped_column(
            Uuid(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )


@declarative_mixin
class SoftDeleteMixin:
    """Provides is_active flag and deleted_at timestamp for soft deletion."""

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


class BaseModelMixin(UUIDMixin, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """A convenient base mixin combining all standard fields."""

    pass
