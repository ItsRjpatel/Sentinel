import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base, BaseModelMixin

class Policy(Base, BaseModelMixin):
    __tablename__ = "policies"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False) # Defender, Firewall, BitLocker, USB, Password, WindowsUpdate, RDP, Power
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(50), nullable=False, default="DRAFT") # DRAFT, ACTIVE, ARCHIVED
    settings = Column(JSON, nullable=False)

    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")
    assignments = relationship("PolicyAssignment", back_populates="policy", cascade="all, delete-orphan")

class PolicyVersion(Base, BaseModelMixin):
    __tablename__ = "policy_versions"

    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    settings = Column(JSON, nullable=False)
    change_summary = Column(Text, nullable=True)

    policy = relationship("Policy", back_populates="versions")

class PolicyAssignment(Base, BaseModelMixin):
    __tablename__ = "policy_assignments"

    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(50), nullable=False) # ENDPOINT or GROUP
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    policy = relationship("Policy", back_populates="assignments")

class PolicyResult(Base, BaseModelMixin):
    __tablename__ = "policy_results"

    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="PENDING") # ENFORCED, CONFLICT, FAILED, PENDING
    applied_at = Column(DateTime, nullable=True)
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    policy = relationship("Policy")
    endpoint = relationship("Endpoint")
