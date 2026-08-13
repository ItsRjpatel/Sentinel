import httpx
import asyncio


async def run():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://127.0.0.1:8000/api/v1/openapi.json")
        schema = r.json()
        print(schema["paths"]["/api/v1/auth/login"]["post"]["requestBody"])


asyncio.run(run())
