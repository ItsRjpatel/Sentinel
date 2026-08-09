# Enterprise Inventory Synchronization Root Cause Report

## 1. Observed Behavior
The Sentinel X UI displays duplicate inventory items for Storage (disks/volumes), Network (adapters), Software, and Services. Hardware and Operating System modules do not suffer from duplication. 

## 2. Investigation Trace
The inventory flow traces as follows:
`Frontend (RUN_INVENTORY)` → `Agent Command Dispatcher` → `WMI Collectors` → `Agent HTTP Client` → `Backend API (/api/v1/inventory/*)` → `Inventory Repositories` → `PostgreSQL Database`.

An inspection of the repository implementations reveals the following pattern:
1. **Is existing inventory deleted before inserting new data?** No. 
2. **Is UPSERT used?** Yes, but it is a **manual, Python-level** upsert. The backend queries `get_by_endpoint()`, maps existing records into a dictionary by a unique key (e.g., `interface_guid`), updates matching records, inserts missing records, and deletes records absent from the incoming payload.
3. **Is INSERT-only used?** No.
4. **Is there a transaction around the refresh?** The service layer wraps the operation in a transaction and commits at the end, but the reads do not use row-level locks (`SELECT ... FOR UPDATE`), leaving them vulnerable to read-modify-write race conditions.
5. **Which repositories are append-only?** None.
6. **Which repositories already replace existing rows correctly?** Hardware and Operating System modules work correctly because they are 1-to-1 relationships and enforce a strict `UNIQUE` constraint on the `endpoint_id` column at the database level.

### Direct Database Queries
Queries executed directly against the PostgreSQL instance confirmed that duplicates are indeed present at the database layer across multiple modules:
- `network_adapter_inventory` (Duplicate `interface_guid`)
- `physical_disk_inventory` (Duplicate `serial_number`)
- `software_inventory` (Duplicate `application_name` + `version`)
- `windows_service_inventory` (Duplicate `service_name`)

## 3. Root Cause Analysis
The duplicates are caused by a combination of a missing database constraint and a fatal flaw in the Python dictionary mapping logic.

**A. Race Conditions (Missing UNIQUE constraints):**
Unlike the Hardware and OS tables, the one-to-many tables (Network, Storage, Software, etc.) **lack composite UNIQUE constraints** for their reconciliation keys. If the backend receives two concurrent `RUN_INVENTORY` uploads for the same endpoint (e.g., caused by UI retries or agent startup bursts), both concurrent requests will execute `get_by_endpoint()`, find 0 existing records, and both will INSERT the same data.

**B. The Dictionary Overwrite Flaw:**
Once the duplicates are inserted into the database, they become permanent. On the next inventory refresh, the repository fetches all records (including duplicates) and builds a dictionary:
```python
existing_map = {item.interface_guid: item for item in existing_items}
```
Because dictionaries cannot hold duplicate keys, the second duplicate simply overwrites the first in memory. 
The reconciliation logic then loops over the incoming data. It finds the key in `existing_map` and updates **one** of the duplicates. 
Finally, the deletion loop (`for key in existing_map: if not incoming, delete`) is skipped because the incoming data *does* contain the key. 
As a result, the orphaned duplicate is neither updated nor deleted, and remains in the database forever.

## 4. Recommended Enterprise Strategy

To provide a robust, concurrency-safe, and consistent synchronization strategy across all inventory modules, the following architectural fixes are required:

### 1. Enforce Database Integrity
We must introduce composite `UNIQUE` constraints to the SQLAlchemy models to strictly reject duplicate insertions at the database engine level.
- `NetworkAdapterInventory`: `UNIQUE(endpoint_id, interface_guid)`
- `PhysicalDiskInventory`: `UNIQUE(endpoint_id, serial_number)`
- `LogicalVolumeInventory`: `UNIQUE(disk_id, volume_guid)`
- `SoftwareInventory`: `UNIQUE(endpoint_id, application_name, publisher, version)`
- `WindowsServiceInventory`: `UNIQUE(endpoint_id, service_name)`
- `WindowsUpdateInventory`: `UNIQUE(endpoint_id, kb_number)`

### 2. Atomic Upserts (Native PostgreSQL)
Replace the flawed Python-level read-modify-write loops with native PostgreSQL atomic upserts using SQLAlchemy's `postgresql.insert().on_conflict_do_update()`. This guarantees atomic synchronization regardless of concurrency.

### 3. Timestamp-based Stale Pruning
Instead of querying and mapping existing items in memory to calculate deletions, the synchronization should be executed as:
1. Generate a single transaction timestamp (`sync_time`).
2. Perform the native `INSERT ... ON CONFLICT DO UPDATE SET updated_at = :sync_time`.
3. Perform a single bulk `DELETE FROM table WHERE endpoint_id = :id AND updated_at < :sync_time`.

This pattern entirely eliminates Python memory overhead, is completely immune to race conditions, and provides a unified, highly performant standard for all enterprise inventory synchronization.
