import httpx
import asyncio

async def run():
    async with httpx.AsyncClient() as client:
        # Test Form Data
        r_form = await client.post('http://127.0.0.1:8000/api/v1/auth/login', data={'username': 'admin', 'password': 'admin123'})
        print("Form response:", r_form.status_code, r_form.text)

        # Test JSON Data
        r_json = await client.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
        print("JSON response:", r_json.status_code, r_json.text)

asyncio.run(run())
