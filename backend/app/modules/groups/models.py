from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModelMixin

class EndpointGroup(Base, BaseModelMixin):
    __tablename__ = "endpoint_groups"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    group_type = Column(String(50), nullable=False, default="STATIC") # STATIC or DYNAMIC
    criteria = Column(JSON, nullable=True) # E.g. {"os": "Windows 11", "site": "HQ", "department": "IT", "tags": ["Security"]}
    site = Column(String(100), nullable=True, index=True)
    location = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True) # E.g. ["Critical", "PCI-DSS"]
    created_by = Column(String(255), nullable=True)

    members = relationship("EndpointGroupMember", back_populates="group", cascade="all, delete-orphan")

class EndpointGroupMember(Base, BaseModelMixin):
    __tablename__ = "endpoint_group_members"

    group_id = Column(String(36), ForeignKey("endpoint_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(String(255), nullable=True)

    group = relationship("EndpointGroup", back_populates="members")
    endpoint = relationship("Endpoint")
