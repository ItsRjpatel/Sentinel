import pytest
import httpx
from agent.collectors.operating_system.models import OperatingSystemInventoryData
from agent.collectors.operating_system.mapper import map_raw_operating_system
from agent.collectors.operating_system.validator import validate_operating_system_data
from agent.collectors.operating_system.collector import OperatingSystemCollector
from agent.scheduler.os_task import OperatingSystemInventoryTask
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

def test_os_mapper_and_types():
    raw_os = {
        "computer_name": "DESKTOP-ABC",
        "os_name": "Microsoft Windows 11 Pro",
        "edition": "Professional",
        "version": "10.0.22621",
        "build_number": "22621",
        "display_version": "22H2",
        "install_date": "20231015092040.000000+120",
        "last_boot_time": "20260728100532.000000+330",
        "uptime_seconds": 3600,
        "system_architecture": "64-bit",
        "product_type": 1,  # Workstation
        "registered_owner": "Owner",
        "registered_organization": "Org",
        "windows_directory": "C:\\Windows",
        "system_directory": "C:\\Windows\\System32",
        "boot_device": "\\Device\\HarddiskVolume1",
        "system_drive": "C:",
        "locale": "0409",
        "time_zone": "UTC+5:30",
        "domain_workgroup": "WORKGROUP",
        "activation_status": "Licensed (Activated)"
    }
    
    dto = map_raw_operating_system(raw_os)
    assert dto.computer_name == "DESKTOP-ABC"
    assert dto.product_type == "Workstation"
    assert dto.uptime_seconds == 3600
    assert dto.activation_status == "Licensed (Activated)"


def test_os_validator_checks():
    valid_dto = OperatingSystemInventoryData(
        computer_name="DESKTOP-ABC",
        os_name="Microsoft Windows 11 Pro",
        edition="Professional",
        version="10.0.22621",
        build_number="22621",
        display_version="22H2",
        install_date="20231015092040.000000+120",
        last_boot_time="20260728100532.000000+330",
        uptime_seconds=3600,
        system_architecture="64-bit",
        product_type="Workstation",
        registered_owner="Owner",
        registered_organization="Org",
        windows_directory="C:\\Windows",
        system_directory="C:\\Windows\\System32",
        boot_device="\\Device\\HarddiskVolume1",
        system_drive="C:",
        locale="0409",
        time_zone="UTC+5:30",
        domain_workgroup="WORKGROUP",
        activation_status="Licensed"
    )
    assert validate_operating_system_data(valid_dto) is True

    # Empty computer name should fail validation
    invalid_name = valid_dto.model_copy(update={"computer_name": ""})
    assert validate_operating_system_data(invalid_name) is False

    # Negative uptime should fail validation
    invalid_uptime = valid_dto.model_copy(update={"uptime_seconds": -5})
    assert validate_operating_system_data(invalid_uptime) is False


def test_os_collector_execution():
    collector = OperatingSystemCollector()
    dto = collector.collect()
    assert isinstance(dto, OperatingSystemInventoryData)
    assert len(dto.computer_name) > 0
    assert dto.uptime_seconds >= 0


@pytest.mark.asyncio
async def test_os_inventory_task_success(tmp_path):
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
    collector = OperatingSystemCollector()
    
    task = OperatingSystemInventoryTask(
        interval_seconds=86400,
        client=client,
        enrollment_manager=enroll_manager,
        collector=collector
    )
    
    await task.execute()
    assert "/inventory/os" in called_path
    await client.close()
