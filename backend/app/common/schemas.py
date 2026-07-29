from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
