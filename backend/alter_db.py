import asyncio
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import text
from app.db.database import engine

async def alter_tables():
    async with engine.begin() as conn:
        print("Altering software_inventory...")
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN application_name TYPE VARCHAR(500);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN publisher TYPE VARCHAR(500);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN version TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN install_date TYPE VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN install_location TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN uninstall_string TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN install_source TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN architecture TYPE VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN language TYPE VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN product_code TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN url_info TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN help_link TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN modify_path TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN install_scope TYPE VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE software_inventory ALTER COLUMN registry_key TYPE VARCHAR(1000);"))

        print("Altering windows_update_inventory...")
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN kb_number TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN title TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN description TYPE VARCHAR(4000);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN support_url TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN update_id TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN operation_result TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN severity TYPE VARCHAR(255);"))
        await conn.execute(text("ALTER TABLE windows_update_inventory ALTER COLUMN source TYPE VARCHAR(255);"))

        print("Altering windows_service_inventory...")
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN service_name TYPE VARCHAR(500);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN display_name TYPE VARCHAR(1000);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN description TYPE VARCHAR(4000);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN executable_path TYPE VARCHAR(2000);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN account_name TYPE VARCHAR(500);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN binary_path TYPE VARCHAR(2000);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN error_control TYPE VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN dependencies TYPE VARCHAR(2000);"))
        await conn.execute(text("ALTER TABLE windows_service_inventory ALTER COLUMN dependent_services TYPE VARCHAR(2000);"))
        print("Done.")

if __name__ == "__main__":
    asyncio.run(alter_tables())
