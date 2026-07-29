import os
import json
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from agent.security.crypto import encrypt, decrypt, IS_WINDOWS

if IS_WINDOWS:
    try:
        import win32security
        import ntsecuritycon as con
    except ImportError:
        pass


class StorageProvider(ABC):
    """Abstract base class for secure local storage of configurations, tokens, and telemetry queues."""

    @abstractmethod
    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt and read configuration/token data associated with the key.
        Returns a dict of decrypted fields, or None if the key doesn't exist.
        """
        pass

    @abstractmethod
    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Encrypt and write config/token/telemetry values atomically.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete the key and associated secure storage.
        """
        pass


class DPAPIJSONStorageProvider(StorageProvider):
    """JSON flat-file storage provider protected by Windows DPAPI and locked down using NTFS ACLs."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _set_permissions(self, file_path: Path) -> None:
        """Lock down file permissions via NTFS ACLs so only SYSTEM, Administrators, and the owner have access."""
        if not IS_WINDOWS:
            # On non-Windows platforms (testing), use standard owner-only permissions (0600)
            try:
                os.chmod(file_path, 0o600)
            except Exception:
                pass
            return

        try:
            import win32api
            import win32security
            
            # Retrieve SIDs for SYSTEM (S-1-5-18) and Builtin Administrators (S-1-5-32-544)
            system_sid = win32security.ConvertStringSidToSid("S-1-5-18")
            admins_sid = win32security.ConvertStringSidToSid("S-1-5-32-544")

            # Retrieve current user SID to avoid locking ourselves out of the file
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_QUERY
            )
            user_sid, _ = win32security.GetTokenInformation(
                token,
                win32security.TokenUser
            )

            sd = win32security.SECURITY_DESCRIPTOR()
            dacl = win32security.ACL()

            # Allow full access exclusively to SYSTEM, Administrators, and the current user
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, system_sid)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins_sid)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, user_sid)

            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                str(file_path),
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
        except Exception:
            # Fallback or log if pywin32 bindings fail or are incomplete in mock environment
            pass

    async def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Decrypts and loads JSON data from file."""
        file_path = self.base_dir / f"{key}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                encrypted_bytes = f.read()

            if not encrypted_bytes:
                return None

            decrypted_bytes = decrypt(encrypted_bytes)
            data_str = decrypted_bytes.decode("utf-8")
            return json.loads(data_str)
        except Exception:
            # Log decryption failure or file corruption return None
            return None

    async def write(self, key: str, data: Dict[str, Any]) -> bool:
        """Encrypts data using DPAPI and performs atomic file writes via swap."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.base_dir / f"{key}.json"

        try:
            data_str = json.dumps(data)
            data_bytes = data_str.encode("utf-8")
            encrypted_bytes = encrypt(data_bytes)

            # Atomic swap write pattern
            temp_fd, temp_path = tempfile.mkstemp(
                dir=str(self.base_dir),
                prefix=f"sentinel_{key}_",
                suffix=".tmp"
            )
            try:
                with os.fdopen(temp_fd, "wb") as tmp_file:
                    tmp_file.write(encrypted_bytes)
                
                # Lock permissions on the temp file before swapping it into place
                self._set_permissions(Path(temp_path))
                
                # Perform atomic rename
                os.replace(temp_path, str(file_path))
                return True
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete the file from disk."""
        file_path = self.base_dir / f"{key}.json"
        if file_path.exists():
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
