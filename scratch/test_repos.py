import asyncio
from typing import List, Dict, Any

from agent.collectors.software.collector import SoftwareCollector
from agent.collectors.services.collector import WindowsServiceCollector
from agent.collectors.network.collector import NetworkCollector
from agent.collectors.windows_updates.collector import WindowsUpdateCollector

# We'll need a valid token. Since we don't have it, we might get 401. Let's see.
# Wait, I can just test the DB repository directly instead of HTTP!
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.modules.inventory.models import Base
from backend.app.modules.inventory.repository import (
    SoftwareInventoryRepository,
    WindowsServiceInventoryRepository,
    WindowsUpdateInventoryRepository,
    NetworkAdapterInventoryRepository
)
from backend.app.modules.inventory.schemas import (
    SoftwareInventoryCreate,
    WindowsServiceInventoryCreate,
    WindowsUpdateInventoryCreate,
    NetworkAdapterInventoryCreate
)
from backend.app.db.session import engine, async_session_maker

async def test_repo():
    agent_id = uuid.uuid4()
    
    import pythoncom
    pythoncom.CoInitialize()
    
    try:
        # Collect
        softs = SoftwareCollector().collect()
        svcs = WindowsServiceCollector().collect()
        nets = NetworkCollector().collect()
        wus = WindowsUpdateCollector().collect()
        
        async with async_session_maker() as session:
            try:
                print("Testing Software Repo...")
                repo = SoftwareInventoryRepository(session)
                data = [SoftwareInventoryCreate.model_validate(x.model_dump()) for x in softs]
                await repo.upsert_software(agent_id, data)
                await session.commit()
                print("Software Repo OK")
            except Exception as e:
                print(f"Software Repo Error: {e}")
                await session.rollback()

            try:
                print("Testing Services Repo...")
                repo = WindowsServiceInventoryRepository(session)
                data = [WindowsServiceInventoryCreate.model_validate(x.model_dump()) for x in svcs]
                await repo.upsert_services(agent_id, data)
                await session.commit()
                print("Services Repo OK")
            except Exception as e:
                print(f"Services Repo Error: {e}")
                await session.rollback()

            try:
                print("Testing Network Repo...")
                repo = NetworkAdapterInventoryRepository(session)
                data = [NetworkAdapterInventoryCreate.model_validate(x.model_dump()) for x in nets]
                await repo.upsert_adapters(agent_id, data)
                await session.commit()
                print("Network Repo OK")
            except Exception as e:
                print(f"Network Repo Error: {e}")
                await session.rollback()

            try:
                print("Testing Windows Updates Repo...")
                repo = WindowsUpdateInventoryRepository(session)
                data = [WindowsUpdateInventoryCreate.model_validate(x.model_dump()) for x in wus]
                await repo.upsert_updates(agent_id, data)
                await session.commit()
                print("Windows Updates Repo OK")
            except Exception as e:
                print(f"Windows Updates Repo Error: {e}")
                await session.rollback()
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    asyncio.run(test_repo())
