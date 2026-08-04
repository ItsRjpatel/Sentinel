import os
import sys
import hashlib
import logging
import subprocess
import asyncio
from typing import Optional, Dict, Any
from agent.communication.client import AgentHTTPClient
from agent.utils.config import load_settings

logger = logging.getLogger("agent.updater")

CURRENT_AGENT_VERSION = "0.9.0"

class AgentAutoUpdater:
    """Manages secure version checks, binary download, SHA256 checksum verification, and background updates."""

    def __init__(self, http_client: AgentHTTPClient):
        self.http_client = http_client
        self.config = load_settings()

    async def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Queries /api/v1/agent/version for newer agent release packages."""
        try:
            resp = await self.http_client.request("GET", "agent/version")
            if resp.status_code != 200:
                logger.warning(f"Version check returned status {resp.status_code}")
                return None

            data = resp.json()
            latest_version = data.get("version", CURRENT_AGENT_VERSION)
            download_url = data.get("download_url")
            expected_sha256 = data.get("sha256")

            if self.is_newer_version(latest_version, CURRENT_AGENT_VERSION):
                logger.info(f"Newer agent version available: {latest_version} (Current: {CURRENT_AGENT_VERSION})")
                return {
                    "version": latest_version,
                    "download_url": download_url,
                    "sha256": expected_sha256
                }
        except Exception as e:
            logger.error(f"Failed to check for agent updates: {e}")
        return None

    def is_newer_version(self, latest: str, current: str) -> bool:
        """Compares version tuples (e.g. 0.9.1 vs 0.9.0)."""
        try:
            l_parts = [int(x) for x in latest.replace("v", "").split(".")]
            c_parts = [int(x) for x in current.replace("v", "").split(".")]
            return l_parts > c_parts
        except Exception:
            return False

    async def download_and_verify(self, download_url: str, expected_sha256: Optional[str] = None) -> Optional[str]:
        """Downloads the installer binary and verifies SHA256 integrity."""
        temp_dir = os.environ.get("TEMP", "C:\\Windows\\Temp")
        installer_path = os.path.join(temp_dir, "SentinelAgentUpdate.exe")

        try:
            logger.info(f"Downloading update binary from {download_url}...")
            resp = await self.http_client.request("GET", download_url)
            if resp.status_code != 200:
                logger.error(f"Binary download failed with status {resp.status_code}")
                return None

            with open(installer_path, "wb") as f:
                f.write(resp.content)

            # Verify checksum if provided
            if expected_sha256:
                sha256_hash = hashlib.sha256()
                with open(installer_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                calculated_hash = sha256_hash.hexdigest()

                if calculated_hash.lower() != expected_sha256.lower():
                    logger.error(f"Checksum mismatch! Expected: {expected_sha256}, Got: {calculated_hash}")
                    os.remove(installer_path)
                    return None

            logger.info(f"Update binary verified successfully: {installer_path}")
            return installer_path
        except Exception as e:
            logger.error(f"Error during update download & verification: {e}")
            return None

    def apply_update(self, installer_path: str):
        """Launches silent update installer executable in detached process."""
        try:
            logger.info(f"Applying agent update silently using {installer_path}...")
            if os.name == "nt":
                subprocess.Popen(f'"{installer_path}" /S', shell=True)
            else:
                logger.info("Auto-update execution only supported on Windows host.")
        except Exception as e:
            logger.error(f"Failed to launch update installer: {e}")
