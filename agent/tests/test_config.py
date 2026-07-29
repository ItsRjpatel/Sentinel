import os
import pytest
from tempfile import TemporaryDirectory
from pathlib import Path
from agent.utils.config import load_settings, AgentSettings

def test_default_settings():
    settings = AgentSettings()
    assert settings.server_url == "http://localhost:8000/api/v1"
    assert settings.heartbeat_interval_seconds == 60
    assert settings.log_level == "INFO"

def test_settings_env_override():
    os.environ["SENTINEL_SERVER_URL"] = "http://test-server/api/v1"
    os.environ["SENTINEL_HEARTBEAT_INTERVAL_SECONDS"] = "30"
    try:
        settings = AgentSettings()
        assert settings.server_url == "http://test-server/api/v1"
        assert settings.heartbeat_interval_seconds == 30
    finally:
        del os.environ["SENTINEL_SERVER_URL"]
        del os.environ["SENTINEL_HEARTBEAT_INTERVAL_SECONDS"]

def test_load_settings_file(tmp_path):
    config_dir = tmp_path / "Sentinel"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    
    config_payload = {
        "server_url": "http://file-server/api/v1",
        "heartbeat_interval_seconds": 15,
        "log_level": "DEBUG"
    }
    
    import json
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_payload, f)
        
    settings = load_settings(data_dir_override=str(config_dir))
    assert settings.server_url == "http://file-server/api/v1"
    assert settings.heartbeat_interval_seconds == 15
    assert settings.log_level == "DEBUG"
