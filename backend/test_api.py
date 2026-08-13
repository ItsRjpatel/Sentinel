import asyncio
import httpx
from sqlalchemy import text
from app.db.session import async_session_maker


async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Clear the table first
        async with async_session_maker() as session:
            await session.execute(text("DELETE FROM refresh_tokens"))
            await session.commit()

        print("Cleared refresh_tokens table")

        # Call Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "TestPassword123!"},
        )
        print("Login status:", response.status_code)
        try:
            print("Login body:", response.json())
        except Exception as e:
            print("Failed to decode json:", response.text)

        # Check DB
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM refresh_tokens"))
            print("Refresh tokens count after login:", result.scalar())

        # Call Refresh
        if response.status_code == 200:
            refresh_token = response.json().get("data", {}).get("refresh_token")
            refresh_res = await client.post(
                "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
            )
            print("Refresh status:", refresh_res.status_code)
            async with async_session_maker() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM refresh_tokens WHERE revoked=false")
                )
                print("Active Refresh tokens count after refresh:", result.scalar())
                result = await session.execute(
                    text("SELECT COUNT(*) FROM refresh_tokens WHERE revoked=true")
                )
                print("Revoked Refresh tokens count after refresh:", result.scalar())

        # Call Logout
        if response.status_code == 200:
            refresh_token = refresh_res.json().get("data", {}).get("refresh_token")
            access_token = refresh_res.json().get("data", {}).get("access_token")
            logout_res = await client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": refresh_token},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print("Logout status:", logout_res.status_code)
            async with async_session_maker() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM refresh_tokens WHERE revoked=false")
                )
                print("Active Refresh tokens count after logout:", result.scalar())


asyncio.run(main())
