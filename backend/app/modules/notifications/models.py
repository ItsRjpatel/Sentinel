import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base, BaseModelMixin

class Notification(Base, BaseModelMixin):
    __tablename__ = "notifications"

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False, default="INFO") # INFO, WARNING, ERROR, CRITICAL
    category = Column(String(50), nullable=False, default="SYSTEM") # SYSTEM, SECURITY, COMMAND, COMPLIANCE
    is_read = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    link = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)

class NotificationPreference(Base, BaseModelMixin):
    __tablename__ = "notification_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    email_address = Column(String(255), nullable=True)
    webhook_enabled = Column(Boolean, nullable=False, default=False)
    webhook_url = Column(String(255), nullable=True)
    slack_enabled = Column(Boolean, nullable=False, default=False)
    slack_webhook_url = Column(String(255), nullable=True)
    teams_enabled = Column(Boolean, nullable=False, default=False)
    teams_webhook_url = Column(String(255), nullable=True)
    min_severity = Column(String(50), nullable=False, default="INFO")
