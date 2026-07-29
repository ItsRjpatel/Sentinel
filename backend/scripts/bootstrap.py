import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure the backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session_maker
from app.modules.auth.repository import PermissionRepository, RoleRepository
from scripts.bootstrap_admin import create_super_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_PERMISSIONS = [
    # Users
    "users.read",
    "users.create",
    "users.update",
    "users.delete",
    # Roles
    "roles.read",
    "roles.create",
    "roles.update",
    "roles.delete",
    # Permissions
    "permissions.read",
    # Auth
    "auth.login",
    "auth.logout",
    "auth.refresh",
    # Endpoints
    "endpoints.read",
    "endpoints.create",
    "endpoints.update",
    "endpoints.delete",
    # Inventory
    "inventory.read",
    "inventory.create",
    "inventory.update",
    "inventory.delete",
    # Monitoring
    "monitoring.read",
    # Commands
    "commands.execute",
    # Security
    "security.read",
    # Compliance
    "compliance.read",
    # Alerts
    "alerts.read",
    "alerts.update",
    # Reports
    "reports.read",
    # Settings
    "settings.read",
    "settings.update",
]

DEFAULT_ROLES = [
    "Super Administrator",
    "Administrator",
    "Security Analyst",
    "Operator",
    "Viewer",
]


async def bootstrap_permissions(permission_repo: PermissionRepository, session):
    logger.info("Bootstrapping permissions...")
    for perm_name in DEFAULT_PERMISSIONS:
        existing = await permission_repo.get_by_name(perm_name)
        if not existing:
            await permission_repo.create(
                {
                    "name": perm_name,
                    "description": f"Auto-generated permission for {perm_name}",
                }
            )
            logger.info(f"Created permission: {perm_name}")
    await session.commit()


async def bootstrap_roles(
    role_repo: RoleRepository, permission_repo: PermissionRepository, session
):
    logger.info("Bootstrapping roles...")
    for role_name in DEFAULT_ROLES:
        existing = await role_repo.get_by_name(role_name)
        if not existing:
            role = await role_repo.create(
                {"name": role_name, "description": f"Auto-generated {role_name} role"}
            )
            logger.info(f"Created role: {role_name}")

            # If Super Administrator, assign all permissions
            if role_name == "Super Administrator":
                # Fetch role again to ensure permissions are loaded (avoid MissingGreenlet on lazy load)
                role = await role_repo.get_by_name(role_name)
                all_perms = await permission_repo.list(limit=1000)
                for p in all_perms:
                    await role_repo.assign_permission(role, p)
                logger.info(f"Assigned all permissions to {role_name}")
    await session.commit()


async def main():
    logger.info("Starting Bootstrap Process...")
    async with async_session_maker() as session:
        permission_repo = PermissionRepository(session)
        role_repo = RoleRepository(session)

        # 1. Create Permissions
        await bootstrap_permissions(permission_repo, session)

        # 2. Create Roles
        await bootstrap_roles(role_repo, permission_repo, session)

        # 3. Create Super Admin
        await create_super_admin(session)

    logger.info("Bootstrap complete.")


if __name__ == "__main__":
    asyncio.run(main())
