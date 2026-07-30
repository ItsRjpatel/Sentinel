import pytest
import httpx
from agent.collectors.network.models import NetworkAdapterInventoryData
from agent.collectors.network.mapper import map_raw_network_adapter
from agent.collectors.network.validator import should_collect_adapter
from agent.collectors.network.collector import NetworkCollector
from agent.scheduler.network_task import NetworkInventoryTask
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

def test_network_mapper_details():
    raw_adapter = {
        "hostname": "TEST-HOST",
        "domain_workgroup": "WORKGROUP",
        "adapter_name": "Wi-Fi 6 Adapter",
        "adapter_description": "Intel(R) Wi-Fi 6 AX201 160MHz",
        "interface_guid": "{1111-2222-3333}",
        "mac_address": "00-11-22-33-44-55",
        "ipv4": "192.168.1.15",
        "ipv6": "fe80::99",
        "subnet_mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns_servers": "1.1.1.1",
        "dhcp_enabled": True,
        "dhcp_server": "192.168.1.1",
        "lease_obtained": "2026-07-29T10:00:00Z",
        "lease_expires": "2026-07-30T10:00:00Z",
        "interface_speed": 866000000,
        "interface_type": "Wireless",
        "operational_status": 2,  # Connected
        "is_physical": True
    }
    
    dto = map_raw_network_adapter(raw_adapter)
    assert dto.mac_address == "00:11:22:33:44:55"
    assert dto.connection_type == "WiFi"
    assert dto.operational_status == "Connected"
    assert dto.is_vpn is False

    # Test VPN mapping
    raw_vpn = dict(raw_adapter)
    raw_vpn["adapter_name"] = "TAP-Windows Adapter V9"
    dto_vpn = map_raw_network_adapter(raw_vpn)
    assert dto_vpn.connection_type == "VPN"
    assert dto_vpn.is_vpn is True


def test_network_filter_validations():
    valid_dto = NetworkAdapterInventoryData(
        hostname="TEST-HOST",
        domain_workgroup="WORKGROUP",
        adapter_name="Ethernet Port 1",
        adapter_description="Intel Gigabit Ethernet",
        interface_guid="{4444-5555}",
        mac_address="00:11:22:33:44:55",
        ipv4="192.168.1.15",
        ipv6="fe80::99",
        subnet_mask="255.255.255.0",
        gateway="192.168.1.1",
        dns_servers="1.1.1.1",
        dhcp_enabled=True,
        dhcp_server="192.168.1.1",
        lease_obtained="2026-07-29T10:00:00Z",
        lease_expires="2026-07-30T10:00:00Z",
        interface_speed=1000000000,
        interface_type="Ethernet",
        operational_status="Connected",
        is_physical=True,
        connection_type="Ethernet",
        is_vpn=False
    )
    
    assert should_collect_adapter(valid_dto) is True

    # Disconnected adapter should be filtered out
    disconnected_dto = valid_dto.model_copy(update={"operational_status": "Disconnected"})
    assert should_collect_adapter(disconnected_dto) is False

    # Loopback IP should be filtered out
    loopback_dto = valid_dto.model_copy(update={"ipv4": "127.0.0.1"})
    assert should_collect_adapter(loopback_dto) is False

    # Docker adapter should be filtered out
    docker_dto = valid_dto.model_copy(update={"adapter_name": "Docker Virtual Port"})
    assert should_collect_adapter(docker_dto) is False

    # Hyper-V internal adapter should be filtered out
    hyperv_dto = valid_dto.model_copy(update={"adapter_name": "vEthernet (Default Switch)"})
    assert should_collect_adapter(hyperv_dto) is False

    # VirtualBox adapter should be filtered out
    vbox_dto = valid_dto.model_copy(update={"adapter_description": "VirtualBox Host-Only Ethernet Adapter"})
    assert should_collect_adapter(vbox_dto) is False


def test_network_collector_execution():
    collector = NetworkCollector()
    adapters = collector.collect()
    assert isinstance(adapters, list)
    for a in adapters:
        assert isinstance(a, NetworkAdapterInventoryData)
        assert a.operational_status == "Connected"


@pytest.mark.asyncio
async def test_network_inventory_task_success(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    # Pre-seed identity to appear enrolled
    await storage.write("identity", {
        "machine_fingerprint": "fake-fingerprint",
        "installation_id": "fake-install-id",
        "agent_uuid": "enrolled-agent-uuid"
    })
    
    called_path = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        called_path.append(request.url.path)
        return httpx.Response(200, json={"success": True})
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    enroll_manager = EnrollmentManager(client=client, storage=storage)
    collector = NetworkCollector()
    
    task = NetworkInventoryTask(
        interval_seconds=86400,
        client=client,
        enrollment_manager=enroll_manager,
        collector=collector
    )
    
    await task.execute()
    assert "/inventory/network" in called_path
    await client.close()
