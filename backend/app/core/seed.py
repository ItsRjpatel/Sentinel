import logging
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.modules.endpoints.models import Endpoint
from app.modules.alerts.models import Alert
from app.modules.commands.models import Command
from app.modules.commands.enums import CommandStatus, CommandType

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def seed_development_data() -> None:
    """
    Backend Development Seeder.
    Checks if endpoints exist in DB; if empty, populates realistic EDR development data
    using backend SQLAlchemy models.
    """
    async with AsyncSessionLocal() as db:
        try:
            res = await db.execute(select(func.count(Endpoint.id)))
            count = res.scalar() or 0

            if count > 0:
                logger.info(
                    f"Database already contains {count} endpoints. Skipping seed."
                )
                return

            logger.info("Database is empty. Populating development seed data...")
            now = utc_now()

            # 1. Endpoints
            seed_endpoints = [
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="WIN11-WKS-01",
                    os_version="Windows 11 Pro 23H2",
                    hardware_hash="hw-hash-win11-001",
                    mac_addresses=["00:15:5D:01:23:45"],
                    ip_addresses=["192.168.1.101"],
                    status="healthy",
                    config_version="1.4.2",
                    last_seen=now,
                ),
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="WIN10-LAP-04",
                    os_version="Windows 10 Enterprise",
                    hardware_hash="hw-hash-win10-004",
                    mac_addresses=["00:15:5D:04:56:78"],
                    ip_addresses=["192.168.1.104"],
                    status="healthy",
                    config_version="1.4.2",
                    last_seen=now - timedelta(minutes=2),
                ),
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="WINSRV-2022-DC",
                    os_version="Windows Server 2022 Datacenter",
                    hardware_hash="hw-hash-srv2022-dc",
                    mac_addresses=["00:15:5D:10:00:01"],
                    ip_addresses=["10.0.0.5"],
                    status="healthy",
                    config_version="1.4.2",
                    last_seen=now - timedelta(seconds=45),
                ),
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="WINSRV-2019-APP",
                    os_version="Windows Server 2019 Standard",
                    hardware_hash="hw-hash-srv2019-app",
                    mac_addresses=["00:15:5D:10:00:12"],
                    ip_addresses=["10.0.0.12"],
                    status="warning",
                    config_version="1.3.9",
                    last_seen=now - timedelta(minutes=1),
                ),
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="MAC-M3-PRO",
                    os_version="macOS Sonoma 14.4.1",
                    hardware_hash="hw-hash-macm3-150",
                    mac_addresses=["A4:83:E7:88:99:AA"],
                    ip_addresses=["192.168.1.150"],
                    status="healthy",
                    config_version="1.4.2",
                    last_seen=now - timedelta(minutes=15),
                ),
                Endpoint(
                    id=uuid.uuid4(),
                    hostname="UBUNTU-24-SRV",
                    os_version="Ubuntu 24.04 LTS",
                    hardware_hash="hw-hash-u24-20",
                    mac_addresses=["52:54:00:12:34:56"],
                    ip_addresses=["10.0.1.20"],
                    status="offline",
                    config_version="1.2.0",
                    last_seen=now - timedelta(hours=4),
                ),
            ]

            for ep in seed_endpoints:
                db.add(ep)
            await db.flush()

            # Map endpoints by hostname for FK linkage
            ep_map = {ep.hostname: ep.id for ep in seed_endpoints}

            # 2. Alerts
            seed_alerts = [
                Alert(
                    id=uuid.uuid4(),
                    title="Unauthorized Access Attempt Blocked",
                    severity="Critical",
                    description="Multiple failed login attempts followed by suspicious process injection into lsass.exe.",
                    endpoint_id=ep_map.get("WINSRV-2019-APP"),
                    endpoint_name="WINSRV-2019-APP",
                    status="active",
                    created_at=now - timedelta(minutes=4),
                ),
                Alert(
                    id=uuid.uuid4(),
                    title="Unsigned Binary Execution Attempt",
                    severity="High",
                    description="Blocked untrusted executable from running out of AppData\\Local\\Temp.",
                    endpoint_id=ep_map.get("WIN10-LAP-04"),
                    endpoint_name="WIN10-LAP-04",
                    status="active",
                    created_at=now - timedelta(minutes=18),
                ),
                Alert(
                    id=uuid.uuid4(),
                    title="Outdated Antivirus Signatures",
                    severity="Medium",
                    description="Endpoint definitions are more than 72 hours behind production policy release.",
                    endpoint_id=ep_map.get("UBUNTU-24-SRV"),
                    endpoint_name="UBUNTU-24-SRV",
                    status="active",
                    created_at=now - timedelta(hours=1),
                ),
                Alert(
                    id=uuid.uuid4(),
                    title="Multiple Failed SSH Attempts",
                    severity="Low",
                    description="Brute force login pattern detected on port 22 from internal subnet.",
                    endpoint_id=ep_map.get("UBUNTU-24-SRV"),
                    endpoint_name="UBUNTU-24-SRV",
                    status="active",
                    created_at=now - timedelta(hours=3),
                ),
            ]

            for a in seed_alerts:
                db.add(a)

            # 3. Commands
            seed_commands = [
                Command(
                    id=uuid.uuid4(),
                    endpoint_id=ep_map.get("WIN11-WKS-01"),
                    command_type=CommandType.SYSTEM_SCAN.value,
                    status=CommandStatus.RUNNING.value,
                    payload={"scan_type": "full", "include_memory": True},
                    created_by="admin",
                    created_at=now - timedelta(minutes=5),
                    started_at=now - timedelta(minutes=4),
                ),
                Command(
                    id=uuid.uuid4(),
                    endpoint_id=ep_map.get("WIN10-LAP-04"),
                    command_type=CommandType.AGENT_UPDATE.value,
                    status=CommandStatus.SUCCESS.value,
                    payload={"target_version": "1.4.2"},
                    created_by="admin",
                    created_at=now - timedelta(minutes=25),
                    started_at=now - timedelta(minutes=24),
                    completed_at=now - timedelta(minutes=22),
                    result={"status": "success", "message": "Agent upgraded to 1.4.2"},
                ),
                Command(
                    id=uuid.uuid4(),
                    endpoint_id=ep_map.get("WINSRV-2022-DC"),
                    command_type=CommandType.PATCH_INSTALL.value,
                    status=CommandStatus.PENDING.value,
                    payload={"kb_article": "KB5031354"},
                    created_by="admin",
                    created_at=now - timedelta(minutes=2),
                ),
                Command(
                    id=uuid.uuid4(),
                    endpoint_id=ep_map.get("WINSRV-2019-APP"),
                    command_type=CommandType.PROCESS_KILL.value,
                    status=CommandStatus.FAILED.value,
                    payload={"pid": 4812, "process_name": "malicious_script.exe"},
                    created_by="admin",
                    created_at=now - timedelta(hours=1),
                    started_at=now - timedelta(hours=1),
                    error_message="Process PID 4812 terminated prior to command execution",
                ),
            ]

            for c in seed_commands:
                db.add(c)

            await db.commit()
            logger.info("Development seed data successfully inserted!")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error seeding development data: {e}")
