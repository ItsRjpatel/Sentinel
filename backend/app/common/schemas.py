from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class CoreModel(BaseModel):
    """Base for all Pydantic models with ORM mode enabled."""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(CoreModel):
    """Schema containing standard timestamps."""

    created_at: datetime
    updated_at: datetime


class BaseResponseSchema(TimestampSchema):
    """Base schema for resources that include UUID, timestamps, and active flags."""

    id: UUID
    is_active: bool


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response wrapper."""

    success: bool = True
    request_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
    data: T | dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standardized error response wrapper."""

    success: bool = False
    request_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_code: str
    message: str
    errors: list[Any] = Field(default_factory=list)
