import pytest
from unittest.mock import MagicMock, patch
from agent.collectors.windows_updates.collector import WindowsUpdateCollector
from agent.collectors.windows_updates.models import WindowsUpdateInventoryData
from agent.collectors.windows_updates.mapper import map_wmi_quick_fix, map_com_update
from agent.collectors.windows_updates.validator import filter_windows_updates

def test_extract_kb_number():
    from agent.collectors.windows_updates.mapper import extract_kb_number
    assert extract_kb_number("KB5031234") == "KB5031234"
    assert extract_kb_number("Update for Windows (kb123456)") == "KB123456"
    assert extract_kb_number("No KB here") == ""

def test_normalize_date():
    from agent.collectors.windows_updates.mapper import normalize_date
    assert normalize_date("02/25/2026") == "2026-02-25"
    assert normalize_date("2026-02-25") == "2026-02-25"
    assert normalize_date("") == "Unknown"

def test_com_mapping():
    raw_com = {
        "Title": "Cumulative Update for Windows 11 Version 23H2 (KB5045678)",
        "Description": "Security update",
        "Category": "Security Updates",
        "LastDeploymentChangeTime": "03/01/2026",
        "SupportUrl": "https://support",
        "UpdateID": "1234-abcd",
        "RevisionNumber": 100,
        "OperationResult": "Succeeded",
        "MsrcSeverity": "Critical",
        "RebootRequired": True,
        "IsHidden": False,
        "IsDownloaded": True,
        "IsInstalled": True,
        "KBArticleIDs": ["5045678"]
    }
    mapped = map_com_update(raw_com)
    assert mapped.kb_number == "KB5045678"
    assert mapped.is_security_update is True
    assert mapped.is_critical_update is True
    assert mapped.requires_restart is True
    assert mapped.installed_state == "Installed"
    assert mapped.source == "COM"
    assert mapped.installed_on == "2026-03-01"

def test_wmi_mapping():
    raw_wmi = {
        "HotFixID": "KB5031234",
        "Description": "Security Update",
        "InstalledBy": "Admin",
        "InstalledOn": "02/25/2026",
        "CSName": "TEST-PC"
    }
    mapped = map_wmi_quick_fix(raw_wmi)
    assert mapped.kb_number == "KB5031234"
    assert mapped.source == "WMI"
    assert mapped.installed_state == "Installed"
    assert mapped.is_security_update is True
    assert mapped.installed_on == "2026-02-25"

def test_filter_windows_updates():
    wmi_data = [
        {"HotFixID": "KB1111111", "Description": "Security Update"},
        {"HotFixID": "KB2222222", "Description": "Update"} # Should be dropped by duplicate rules if in COM
    ]
    
    com_data = [
        {"Title": "Update KB2222222", "KBArticleIDs": ["2222222"], "IsInstalled": True},
        {"Title": "Failed Update KB3333333", "KBArticleIDs": ["3333333"], "IsInstalled": False}, # Dropped
        {"Title": "Invalid No KB"} # Dropped
    ]
    
    dtos = filter_windows_updates(wmi_data, com_data, map_wmi_quick_fix, map_com_update)
    assert len(dtos) == 2
    
    kbs = [d.kb_number for d in dtos]
    assert "KB2222222" in kbs
    assert "KB1111111" in kbs
    
    # Assert KB2222222 came from COM (priority)
    kb2 = next(d for d in dtos if d.kb_number == "KB2222222")
    assert kb2.source == "COM"

@patch('agent.collectors.windows_updates.collector.IS_WINDOWS', False)
def test_windows_update_collector_non_windows():
    collector = WindowsUpdateCollector()
    results = collector.collect()
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], WindowsUpdateInventoryData)
