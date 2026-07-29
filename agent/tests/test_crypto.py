import pytest
from pathlib import Path
from agent.security.crypto import encrypt, decrypt
from agent.utils.storage import DPAPIJSONStorageProvider

def test_dpapi_encrypt_decrypt_roundtrip():
    raw_data = b"SensitiveAgentSecretToken123!"
    encrypted = encrypt(raw_data)
    assert encrypted != raw_data
    
    decrypted = decrypt(encrypted)
    assert decrypted == raw_data

@pytest.mark.asyncio
async def test_json_storage_provider(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    key = "session_tokens"
    data = {
        "access_token": "abc.123.xyz",
        "refresh_token": "refresh-hex-value",
        "expires_in": 3600
    }
    
    # Write data
    success = await storage.write(key, data)
    assert success is True
    
    # Verify file exists on disk
    file_path = tmp_path / f"{key}.json"
    assert file_path.exists()
    
    # Read and assert contents match
    read_data = await storage.read(key)
    assert read_data == data
    
    # Delete data
    deleted = await storage.delete(key)
    assert deleted is True
    assert not file_path.exists()
    
    # Read after delete returns None
    read_again = await storage.read(key)
    assert read_again is None
