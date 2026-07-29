import uuid
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import BaseModelMixin
from app.db.base import Base

class HardwareInventory(Base, BaseModelMixin):
    """Database model storing endpoint hardware specifications and configuration states."""
    __tablename__ = "hardware_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_version: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_release_date: Mapped[str] = mapped_column(String(255), nullable=False)
    motherboard: Mapped[str] = mapped_column(String(255), nullable=False)
    cpu_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cpu_architecture: Mapped[str] = mapped_column(String(100), nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_logical_processors: Mapped[int] = mapped_column(Integer, nullable=False)
    installed_ram_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tpm_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    secure_boot_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_virtual: Mapped[bool] = mapped_column(Boolean, nullable=False)
