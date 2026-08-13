import asyncio
import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.db.session import async_session_maker
from sqlalchemy import select
from app.modules.auth.models import User
from app.core.security import get_password_hash


async def main():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        if user:
            user.password_hash = get_password_hash("admin123")
            await session.commit()
            print("Admin password updated successfully in the database.")
        else:
            print("Admin user not found. Run bootstrap to create one.")


if __name__ == "__main__":
    asyncio.run(main())
