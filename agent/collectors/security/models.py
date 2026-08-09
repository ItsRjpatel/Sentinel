from pydantic import BaseModel, Field
from typing import Optional

class SecurityInventoryData(BaseModel):
    defender_enabled: bool = Field(..., description="Is Microsoft Defender Antivirus enabled")
    real_time_protection_enabled: bool = Field(..., description="Is Real-Time Protection enabled")
    defender_service_status: str = Field(..., description="Status of WinDefend service")
    antivirus_signature_version: str = Field(..., description="AV signature version")
    firewall_domain_enabled: bool = Field(..., description="Is Domain profile firewall enabled")
    firewall_private_enabled: bool = Field(..., description="Is Private profile firewall enabled")
    firewall_public_enabled: bool = Field(..., description="Is Public profile firewall enabled")
