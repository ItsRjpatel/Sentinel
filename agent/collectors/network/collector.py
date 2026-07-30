import os
import logging
from typing import List, Dict, Any
from agent.collectors.network.models import NetworkAdapterInventoryData
from agent.collectors.network.mapper import map_raw_network_adapter
from agent.collectors.network.validator import should_collect_adapter

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"


class NetworkCollector:
    """Queries native Windows WMI tables to retrieve active network adapter telemetry."""

    def collect(self) -> List[NetworkAdapterInventoryData]:
        """Runs the WMI query collection routines and returns filtered, validated DTOs."""
        raw_adapters: List[Dict[str, Any]] = []

        if not IS_WINDOWS:
            # Stub values for cross-platform local developer environments (like MacOS/Linux)
            logger.info("Collector executing on non-Windows platform. Returning stub network adapter inventory data.")
            stub_records = [
                {
                    "hostname": "Standard-Dev-Host",
                    "domain_workgroup": "WORKGROUP",
                    "adapter_name": "Ethernet Adapter 1",
                    "adapter_description": "Intel(R) Ethernet Connection I219-LM",
                    "interface_guid": "{F4A2B8C6-D2E4-4F9A-B0C8-A1D2E3F4B5C6}",
                    "mac_address": "00-11-22-33-44-55",
                    "ipv4": "192.168.1.100",
                    "ipv6": "fe80::11",
                    "subnet_mask": "255.255.255.0",
                    "gateway": "192.168.1.1",
                    "dns_servers": "8.8.8.8, 8.8.4.4",
                    "dhcp_enabled": True,
                    "dhcp_server": "192.168.1.1",
                    "lease_obtained": "2026-07-29T10:00:00Z",
                    "lease_expires": "2026-07-30T10:00:00Z",
                    "interface_speed": 1000000000,
                    "interface_type": "Ethernet",
                    "operational_status": 2,  # Connected
                    "is_physical": True
                }
            ]
            dtos = [map_raw_network_adapter(r) for r in stub_records]
            return [d for d in dtos if should_collect_adapter(d)]

        import win32com.client

        # 1. Connect to WMI root\CIMV2 namespace
        try:
            wmi = win32com.client.GetObject("winmgmts:")
        except Exception as e:
            logger.error(f"Failed to bind WMI engine COM objects: {e}")
            raise RuntimeError("WMI connection unavailable") from e

        # Query Win32_NetworkAdapterConfiguration details
        config_map: Dict[int, Any] = {}
        try:
            config_query = (
                "Select Index, IPAddress, IPSubnet, DefaultIPGateway, DNSServerSearchOrder, "
                "DHCPEnabled, DHCPServer, DHCPLeaseObtained, DHCPLeaseExpires, DNSHostName, DNSDomain "
                "from Win32_NetworkAdapterConfiguration"
            )
            for conf in wmi.ExecQuery(config_query):
                config_map[int(conf.Index)] = conf
        except Exception as e:
            logger.warning(f"Failed to query Win32_NetworkAdapterConfiguration: {e}")

        # Query Win32_NetworkAdapter details
        try:
            adapter_query = (
                "Select DeviceID, GUID, Name, Description, MACAddress, Speed, "
                "AdapterType, NetConnectionStatus, PhysicalAdapter from Win32_NetworkAdapter"
            )
            for adapter in wmi.ExecQuery(adapter_query):
                try:
                    dev_id = int(adapter.DeviceID)
                except (ValueError, TypeError):
                    continue

                # Fetch matching configuration parameters
                conf = config_map.get(dev_id)
                if not conf:
                    continue

                # Ensure we have active IP Addresses
                ips = conf.IPAddress
                if not ips or len(ips) == 0:
                    continue

                # Extract IPv4 and IPv6
                ipv4_val = "0.0.0.0"
                ipv6_val = "::"
                for ip in ips:
                    if ":" in ip:
                        ipv6_val = ip
                    else:
                        ipv4_val = ip

                # Subnet Mask mapping
                subnets = conf.IPSubnet
                subnet_val = "255.255.255.0"
                if subnets and len(subnets) > 0:
                    subnet_val = subnets[0]

                # Default Gateway mapping
                gateways = conf.DefaultIPGateway
                gateway_val = "0.0.0.0"
                if gateways and len(gateways) > 0:
                    gateway_val = gateways[0]

                # DNS Servers mapping
                dns_order = conf.DNSServerSearchOrder
                dns_val = "8.8.8.8"
                if dns_order and len(dns_order) > 0:
                    dns_val = ", ".join(dns_order)

                raw_record = {
                    "hostname": conf.DNSHostName if conf.DNSHostName else "Unknown",
                    "domain_workgroup": conf.DNSDomain if conf.DNSDomain else "WORKGROUP",
                    "adapter_name": adapter.Name,
                    "adapter_description": adapter.Description,
                    "interface_guid": adapter.GUID if adapter.GUID else f"{{{dev_id}}}",
                    "mac_address": adapter.MACAddress,
                    "ipv4": ipv4_val,
                    "ipv6": ipv6_val,
                    "subnet_mask": subnet_val,
                    "gateway": gateway_val,
                    "dns_servers": dns_val,
                    "dhcp_enabled": bool(conf.DHCPEnabled),
                    "dhcp_server": conf.DHCPServer if conf.DHCPServer else "0.0.0.0",
                    "lease_obtained": conf.DHCPLeaseObtained if conf.DHCPLeaseObtained else "",
                    "lease_expires": conf.DHCPLeaseExpires if conf.DHCPLeaseExpires else "",
                    "interface_speed": adapter.Speed if adapter.Speed else 0,
                    "interface_type": adapter.AdapterType if adapter.AdapterType else "Ethernet",
                    "operational_status": adapter.NetConnectionStatus,
                    "is_physical": bool(adapter.PhysicalAdapter)
                }
                raw_adapters.append(raw_record)
        except Exception as e:
            logger.warning(f"Failed to query Win32_NetworkAdapter: {e}")

        # Map and filter using validation rules
        collected = []
        for raw in raw_adapters:
            try:
                dto = map_raw_network_adapter(raw)
                if should_collect_adapter(dto):
                    collected.append(dto)
            except Exception as ex:
                logger.error(f"Error mapping network adapter raw properties: {ex}")

        return collected
