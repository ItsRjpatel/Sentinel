import pytest
from unittest.mock import MagicMock, patch
from agent.collectors.software.models import SoftwareInventoryData
from agent.collectors.software.mapper import map_raw_registry_entry, normalize_install_date, normalize_publisher, normalize_architecture
from agent.collectors.software.validator import filter_software_list, is_valid_software_entry
from agent.scheduler.software_task import SoftwareInventoryTask

def test_normalize_install_date():
    assert normalize_install_date("20260115") == "2026-01-15"
    assert normalize_install_date("2026-01-15") == "2026-01-15"
    assert normalize_install_date("") == "Unknown"


def test_normalize_publisher():
    assert normalize_publisher("Microsoft Corp") == "Microsoft Corporation"
    assert normalize_publisher("Google Inc") == "Google LLC"
    assert normalize_publisher(None) == "Unknown Publisher"


def test_normalize_architecture():
    assert normalize_architecture(None, r"Software\WOW6432Node\Uninstall") == "x86"
    assert normalize_architecture("x64") == "x64"
    assert normalize_architecture("x86") == "x86"


def test_map_raw_registry_entry():
    raw = {
        "DisplayName": "Test Software 1.0",
        "Publisher": "Test Corp",
        "DisplayVersion": "1.0.0",
        "InstallDate": "20260101",
        "InstallLocation": "C:\\Program Files\\Test",
        "EstimatedSize": 1024,
        "UninstallString": "C:\\Program Files\\Test\\uninstall.exe",
        "InstallSource": "",
        "Architecture": "x64",
        "Language": "1033",
        "ProductCode": "{TEST-GUID}",
        "SystemComponent": 0,
        "WindowsInstaller": 1,
        "URLInfoAbout": "https://test.com",
        "HelpLink": "",
        "ModifyPath": "",
        "InstallScope": "Per-machine",
        "RegistryKey": "HKLM\\Software\\Test"
    }

    dto = map_raw_registry_entry(raw)
    assert dto.application_name == "Test Software 1.0"
    assert dto.publisher == "Test Corp"
    assert dto.version == "1.0.0"
    assert dto.install_date == "2026-01-01"
    assert dto.estimated_size_kb == 1024
    assert dto.windows_installer is True
    assert dto.system_component is False


def test_validator_filtering():
    raw_valid = {
        "DisplayName": "Valid App",
        "Publisher": "Vendor",
        "DisplayVersion": "1.0",
        "SystemComponent": 0
    }
    raw_no_name = {
        "Publisher": "Vendor"
    }
    raw_sys_comp = {
        "DisplayName": "System Component App",
        "SystemComponent": 1
    }
    raw_kb_update = {
        "DisplayName": "Security Update for Windows (KB5031234)",
        "SystemComponent": 0
    }
    raw_lang_pack = {
        "DisplayName": "Microsoft Windows Language Pack - fr-FR",
        "SystemComponent": 0
    }
    raw_driver = {
        "DisplayName": "Realtek High Definition Audio Driver Package",
        "Publisher": "Realtek",
        "SystemComponent": 0
    }

    entries = [raw_valid, raw_no_name, raw_sys_comp, raw_kb_update, raw_lang_pack, raw_driver, raw_valid]
    filtered = filter_software_list(entries, map_raw_registry_entry)

    assert len(filtered) == 1
    assert filtered[0].application_name == "Valid App"


@pytest.mark.asyncio
async def test_software_task_execution():
    client_mock = AsyncMock()
    client_mock.request.return_value.status_code = 200

    enrollment_mock = AsyncMock()
    enrollment_mock.is_enrolled.return_value = True

    collector_mock = MagicMock()
    collector_mock.collect.return_value = [
        SoftwareInventoryData(
            application_name="Stub App",
            publisher="Stub Vendor",
            version="1.0.0",
            install_date="2026-01-01",
            install_location="C:\\Stub",
            estimated_size_kb=100,
            uninstall_string="uninstall.exe",
            install_source="",
            architecture="x64",
            language="1033",
            product_code="",
            system_component=False,
            windows_installer=False,
            url_info="",
            help_link="",
            modify_path="",
            install_scope="Per-machine",
            registry_key="HKLM\\Software\\Stub"
        )
    ]

    task = SoftwareInventoryTask(
        interval_seconds=86400,
        client=client_mock,
        enrollment_manager=enrollment_mock,
        collector=collector_mock
    )
    await task.execute()

    client_mock.request.assert_called_once()
    _, kwargs = client_mock.request.call_args
    assert kwargs["path"] == "inventory/software"
    assert len(kwargs["json_data"]) == 1
    assert kwargs["json_data"][0]["application_name"] == "Stub App"


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
