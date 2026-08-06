import os
import json
from pathlib import Path
from typing import Any, Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AgentSettings(BaseSettings):
    """Pydantic-based configuration model for Sentinel Windows Agent."""
    
    model_config = SettingsConfigDict(
        env_prefix="SENTINEL_",
        env_file=".env",
        extra="ignore"
    )

    server_url: str = Field(default="http://localhost:8000/api/v1")
    heartbeat_interval_seconds: int = Field(default=60)
    log_level: str = Field(default="INFO")
    data_dir: str = Field(default="")
    config_version: str = Field(default="1.0.0")
    enrollment_secret: str = Field(default="")
    verify_tls: bool = Field(default=True)

    def get_data_dir(self) -> Path:
        """Retrieve the local directory path for storing identity and config data."""
        if self.data_dir:
            path = Path(self.data_dir)
        else:
            prog_data = os.environ.get("ProgramData")
            if prog_data:
                path = Path(prog_data) / "EndpointSentinel"
            else:
                # Local directory fallback for development/testing
                path = Path(__file__).resolve().parents[2] / "data"
        return path

    def get_config_file_path(self) -> Path:
        return self.get_data_dir() / "config.json"

    def get_identity_file_path(self) -> Path:
        return self.get_data_dir() / "identity.json"

    def get_log_file_path(self) -> Path:
        return self.get_data_dir() / "logs" / "agent.log"


def load_settings(data_dir_override: str = "") -> AgentSettings:
    """Loads settings from config.json, merging defaults and environment overrides."""
    kwargs = {}
    if data_dir_override:
        kwargs["data_dir"] = data_dir_override
    temp_settings = AgentSettings(**kwargs)
    config_path = temp_settings.get_config_file_path()
    
    config_data: Dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                # Check if it starts with JSON syntax
                content = f.read().strip()
                if content.startswith("{"):
                    config_data = json.loads(content)
        except Exception:
            # Fallback to defaults on corrupt config.json
            pass

    if data_dir_override:
        config_data["data_dir"] = data_dir_override

    return AgentSettings(**config_data)
