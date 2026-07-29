import pytest
from pathlib import Path
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.security.identity import (
    generate_machine_fingerprint,
    get_hardware_identifiers,
    load_or_create_identity
)

def test_machine_fingerprint_generation():
    fingerprint1 = generate_machine_fingerprint()
    fingerprint2 = generate_machine_fingerprint()
    
    assert fingerprint1 != ""
    # Must be a valid SHA-256 hex string (64 characters)
    assert len(fingerprint1) == 64
    # Must be stable across multiple executions
    assert fingerprint1 == fingerprint2

def test_hardware_identifiers_contain_data():
    ids = get_hardware_identifiers()
    assert "bios_uuid" in ids
    assert "mac_address" in ids
    assert ids["bios_uuid"] != ""
    assert ids["mac_address"] != ""

@pytest.mark.asyncio
async def test_identity_persistence(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    
    # First load must generate new identity values
    id1 = await load_or_create_identity(storage)
    assert id1.agent_uuid is None
    assert id1.machine_fingerprint != ""
    assert id1.installation_id != ""
    
    # Verify file is written
    file_path = tmp_path / "identity.json"
    assert file_path.exists()
    
    # Second load must return identical cached values (persistence check)
    id2 = await load_or_create_identity(storage)
    assert id1.machine_fingerprint == id2.machine_fingerprint
    assert id1.installation_id == id2.installation_id
    assert id2.agent_uuid is None
