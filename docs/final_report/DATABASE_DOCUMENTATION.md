# DATABASE DOCUMENTATION

The PostgreSQL database uses Alembic for schema migrations.

## Important Design Decisions
- **UUIDs as Primary Keys**: Used for `endpoints` to obscure sequential growth and prevent enumeration attacks.
- **Async Driver**: Utilizes `asyncpg` to prevent blocking the FastAPI event loop during high-volume telemetry ingestion.

## Relationships
- One-to-One: `endpoints` to `hardware_inventory` and `os_inventory`.
- One-to-Many: `endpoints` to `telemetry`, `alerts`, and `commands`.

## Indexes
- Indexed `endpoint_id` and `recorded_at` in the `telemetry` table for fast time-series queries.
- Indexed `status` in the `commands` table to quickly identify pending jobs.
