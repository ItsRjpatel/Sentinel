import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.modules.auth.repository import RoleRepository, UserRepository

logger = logging.getLogger(__name__)


async def create_super_admin(session: AsyncSession) -> None:
    logger.info("Creating Super Administrator...")

    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")
    if not password:
        logger.error(
            "BOOTSTRAP_ADMIN_PASSWORD environment variable is not set. Skipping admin creation."
        )
        return

    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)

    # Check if admin already exists
    existing_admin = await user_repo.get_by_username("admin")
    if existing_admin:
        logger.info("Admin user already exists. Skipping creation.")
        return

    # Create admin user
    # Note: We hash using the existing security utilities
    password_hash = get_password_hash(password)

    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": password_hash,
        "is_active": True,
        "is_verified": True,
    }

    try:
        user = await user_repo.create(admin_data)
        logger.info("Created user 'admin'.")

        # Assign Super Administrator role
        super_admin_role = await role_repo.get_by_name("Super Administrator")
        if super_admin_role:
            await user_repo.assign_role(user, super_admin_role)
            logger.info("Assigned 'Super Administrator' role to 'admin'.")
        else:
            logger.warning(
                "Role 'Super Administrator' not found! Could not assign to admin."
            )

        await session.commit()
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        await session.rollback()
        raise
