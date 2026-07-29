import pytest
from agent.collectors.hardware.models import HardwareInventoryData
from agent.collectors.hardware.mapper import map_raw_hardware
from agent.collectors.hardware.validator import validate_hardware_data
from agent.collectors.hardware.collector import HardwareCollector

def test_mapper_cpu_and_vm_detection():
    # Test typical VM properties
    raw_vm = {
        "manufacturer": "innotek GmbH",
        "model": "VirtualBox",
        "serial_number": "0",
        "bios_version": "VirtualBox Version 1.0",
        "bios_manufacturer": "Oracle Corporation",
        "bios_release_date": "2006-12-01",
        "motherboard": "Standard Board",
        "cpu_name": "Intel Core i7-10700 CPU @ 2.90GHz",
        "cpu_architecture": 9,  # x64
        "cpu_cores": 2,
        "cpu_logical_processors": 4,
        "installed_ram_bytes": 8589934592,  # 8 GB
        "tpm_version": None,
        "secure_boot_enabled": False
    }

    dto = map_raw_hardware(raw_vm)
    assert dto.cpu_architecture == "x64"
    assert dto.is_virtual is True
    assert dto.manufacturer == "innotek GmbH"
    assert dto.installed_ram_bytes == 8589934592

    # Test physical x86 device properties
    raw_physical = {
        "manufacturer": "Dell Inc.",
        "model": "OptiPlex 7080",
        "serial_number": "MXL123",
        "cpu_architecture": 0,  # x86
        "installed_ram_bytes": 16000000000
    }
    dto_phys = map_raw_hardware(raw_physical)
    assert dto_phys.cpu_architecture == "x86"
    assert dto_phys.is_virtual is False


def test_validator_logic_checks():
    valid_dto = HardwareInventoryData(
        manufacturer="HP",
        model="EliteBook 840",
        serial_number="5CG12345",
        bios_version="01.02.03",
        bios_manufacturer="HP BIOS",
        bios_release_date="2024-01-01",
        motherboard="840-BOARD",
        cpu_name="Intel Core i5-1135G7",
        cpu_architecture="x64",
        cpu_cores=4,
        cpu_logical_processors=8,
        installed_ram_bytes=17179869184,
        tpm_version="2.0",
        secure_boot_enabled=True,
        is_virtual=False
    )
    assert validate_hardware_data(valid_dto) is True

    # Logical processors less than physical cores should fail semantic check
    invalid_cpu = valid_dto.model_copy(update={"cpu_logical_processors": 2})
    assert validate_hardware_data(invalid_cpu) is False

    # Zero RAM should fail semantic check
    invalid_ram = valid_dto.model_copy(update={"installed_ram_bytes": 0})
    assert validate_hardware_data(invalid_ram) is False


def test_collector_execution():
    collector = HardwareCollector()
    dto = collector.collect()
    assert isinstance(dto, HardwareInventoryData)
    assert dto.cpu_cores >= 1
    assert dto.installed_ram_bytes >= 0
