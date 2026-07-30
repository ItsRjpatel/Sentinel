import pytest
from unittest.mock import MagicMock, patch
from agent.collectors.services.collector import WindowsServiceCollector
from agent.collectors.services.models import WindowsServiceInventoryData
from agent.collectors.services.mapper import map_wmi_service
from agent.collectors.services.validator import filter_windows_services

def test_wmi_mapping():
    raw_wmi = {
        "Name": "Spooler",
        "DisplayName": "Print Spooler",
        "Description": "Spools print jobs.",
        "PathName": "C:\\Windows\\System32\\spoolsv.exe",
        "State": "Running",
        "StartMode": "Auto",
        "ServiceType": "Own Process",
        "StartName": "LocalSystem",
        "ProcessId": 1234,
        "DelayedAutoStart": False,
        "ErrorControl": "Normal",
        "AcceptStop": True,
        "AcceptPause": False,
        "DesktopInteract": False,
        "TagId": 0
    }
    mapped = map_wmi_service(raw_wmi)
    assert mapped.service_name == "Spooler"
    assert mapped.display_name == "Print Spooler"
    assert mapped.current_state == "Running"
    assert mapped.start_mode == "Auto"
    assert mapped.process_id == 1234
    assert mapped.can_stop is True
    assert mapped.can_pause is False

def test_filter_windows_services():
    wmi_data = [
        {"Name": "Spooler", "DisplayName": "Print Spooler", "ServiceType": "Own Process"},
        {"Name": "CDPUserSvc_1a2b3c", "DisplayName": "Connected Devices Platform User Service", "ServiceType": "Share Process"}, # Temporary service, should be dropped
        {"Name": "ACPI", "DisplayName": "Microsoft ACPI Driver", "ServiceType": "Kernel Driver"}, # Driver service, should be dropped
        {"Name": "WinDefend", "DisplayName": "Windows Defender", "ServiceType": "Own Process"},
        {"Name": "WinDefend", "DisplayName": "Duplicate Entry", "ServiceType": "Own Process"} # Duplicate, should be dropped
    ]
    
    dtos = filter_windows_services(wmi_data, map_wmi_service)
    assert len(dtos) == 2
    
    names = [d.service_name for d in dtos]
    assert "Spooler" in names
    assert "WinDefend" in names
    assert "CDPUserSvc_1a2b3c" not in names
    assert "ACPI" not in names

@patch('agent.collectors.services.collector.IS_WINDOWS', False)
def test_windows_service_collector_non_windows():
    collector = WindowsServiceCollector()
    results = collector.collect()
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], WindowsServiceInventoryData)
