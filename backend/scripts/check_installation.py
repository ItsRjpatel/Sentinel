import asyncio
import os
import sys

from sqlalchemy import text

# Ensure the backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session_maker
from app.modules.auth.repository import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from scripts.bootstrap import DEFAULT_PERMISSIONS, DEFAULT_ROLES


async def check_installation():
    checks = {
        "Database Connection": False,
        "Alembic Migrations": False,
        "Environment Variables": False,
        "Super Administrator": False,
        "Default Roles": False,
        "Default Permissions": False,
    }

    # 1. Environment Variables
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")
    jwt_secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY")
    if password and jwt_secret:
        checks["Environment Variables"] = True
    else:
        if not password:
            print("FAIL: BOOTSTRAP_ADMIN_PASSWORD not set in environment.")
        if not jwt_secret:
            print("FAIL: JWT_SECRET_KEY (or SECRET_KEY) not set in environment.")

    # 2. Database & Migrations & Data
    try:
        async with async_session_maker() as session:
            # Check DB Connection
            await session.execute(text("SELECT 1"))
            checks["Database Connection"] = True

            # Check Alembic Migrations
            try:
                result = await session.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                version = result.scalar()
                if version:
                    checks["Alembic Migrations"] = True
            except Exception:
                print("FAIL: Alembic version table not found. Migrations not applied.")

            # Check Default Permissions
            perm_repo = PermissionRepository(session)
            missing_perms = []
            for perm in DEFAULT_PERMISSIONS:
                p = await perm_repo.get_by_name(perm)
                if not p:
                    missing_perms.append(perm)

            if not missing_perms:
                checks["Default Permissions"] = True
            else:
                print(f"FAIL: Missing permissions: {missing_perms}")

            # Check Default Roles
            role_repo = RoleRepository(session)
            missing_roles = []
            for role_name in DEFAULT_ROLES:
                r = await role_repo.get_by_name(role_name)
                if not r:
                    missing_roles.append(role_name)

            if not missing_roles:
                checks["Default Roles"] = True
            else:
                print(f"FAIL: Missing roles: {missing_roles}")

            # Check Super Administrator
            user_repo = UserRepository(session)
            admin = await user_repo.get_by_username("admin")
            if admin:
                checks["Super Administrator"] = True
            else:
                print("FAIL: Super Administrator 'admin' not found.")

    except Exception as e:
        print(f"FAIL: Database connection failed: {e}")

    # Summary Output
    print("\n--- Installation Verification Summary ---")
    all_passed = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"[{status}] {check}")

    print("-----------------------------------------")
    if all_passed:
        print("OVERALL STATUS: PASS")
        sys.exit(0)
    else:
        print("OVERALL STATUS: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_installation())
