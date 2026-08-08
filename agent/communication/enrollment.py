import socket
import platform
import logging
from typing import Any, Dict, List
from agent.communication.client import AgentHTTPClient
from agent.utils.storage import StorageProvider
from agent.security.identity import load_or_create_identity, get_hardware_identifiers

logger = logging.getLogger(__name__)


def get_enrollment_payload(identity: AgentIdentity) -> Dict[str, Any]:
    """Assembles OS and hardware identifiers for enrollment payload."""
    hostname = socket.gethostname()
    os_ver = f"{platform.system()} {platform.release()} (Build {platform.version()})"
    
    ids = get_hardware_identifiers()
    macs = [ids["mac_address"]] if ids["mac_address"] else []
    
    ips: List[str] = []
    try:
        ips = socket.gethostbyname_ex(hostname)[2]
    except Exception:
        pass

    return {
        "hostname": hostname,
        "os_version": os_ver,
        "agent_id": identity.agent_uuid,
        "hardware_hash": identity.machine_fingerprint,
        "identity_version": identity.identity_version,
        "mac_addresses": macs,
        "ip_addresses": ips
    }


class EnrollmentManager:
    """Manages the one-time registration handshake with the Sentinel backend."""

    def __init__(
        self,
        client: AgentHTTPClient,
        storage: StorageProvider,
        enrollment_secret: str = ""
    ) -> None:
        self.client = client
        self.storage = storage
        self.enrollment_secret = enrollment_secret

    async def is_enrolled(self) -> bool:
        """Checks if the agent has valid session credentials saved in secure storage."""
        tokens = await self.storage.read("tokens")
        if not tokens:
            return False
        return bool(tokens.get("access_token") and tokens.get("refresh_token"))

    async def enroll(self) -> str:
        """Executes the registration POST and persists the returned credentials."""
        identity = await load_or_create_identity(self.storage)
        logger.info(f"Initiating agent registration handshake for {identity.agent_uuid}...")
        payload = get_enrollment_payload(identity)
        
        headers = {}
        if self.enrollment_secret:
            headers["X-Enrollment-Secret"] = self.enrollment_secret

        # Enrolls with endpoint route
        resp = await self.client.request(
            method="POST",
            path="endpoints/enroll",
            json_data=payload,
            headers=headers
        )

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Registration failed with HTTP status code: {resp.status_code}")

        res_data = resp.json()
        if not res_data.get("success"):
            raise RuntimeError(f"Registration rejected: {res_data.get('message')}")

        data = res_data.get("data", {})
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        if not access_token or not refresh_token:
            raise ValueError("Registration response missing required session credentials.")

        # Save tokens to secure DPAPI JSON storage
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        await self.storage.write("tokens", tokens)

        logger.info(f"Enrollment successful. Assigned Agent UUID: {identity.agent_uuid}")
        return identity.agent_uuid
