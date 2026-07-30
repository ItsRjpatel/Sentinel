from typing import Optional
from pydantic import BaseModel, Field

class NetworkAdapterInventoryData(BaseModel):
    """Pydantic validated DTO containing aggregated endpoint network adapter details."""
    hostname: str = Field(..., max_length=255)
    domain_workgroup: str = Field(..., max_length=255)
    adapter_name: str = Field(..., max_length=255)
    adapter_description: str = Field(..., max_length=255)
    interface_guid: str = Field(..., max_length=100)
    mac_address: Optional[str] = Field(None, max_length=100)
    ipv4: str = Field(..., max_length=100)
    ipv6: str = Field(..., max_length=200)
    subnet_mask: str = Field(..., max_length=100)
    gateway: str = Field(..., max_length=100)
    dns_servers: str = Field(..., max_length=500)
    dhcp_enabled: bool
    dhcp_server: str = Field(..., max_length=100)
    lease_obtained: str = Field(..., max_length=100)
    lease_expires: str = Field(..., max_length=100)
    interface_speed: int = Field(..., ge=0)
    interface_type: str = Field(..., max_length=100)
    operational_status: str = Field(..., max_length=50)
    is_physical: bool
    connection_type: str = Field(..., max_length=50)
    is_vpn: bool
