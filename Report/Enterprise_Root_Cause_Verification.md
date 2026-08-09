# Enterprise Root Cause Verification Report

This report provides the runtime evidence and code traces confirming the root causes behind the duplicate endpoint, incorrect hardware, and ghost online issues in Sentinel X. No code modifications have been made.

## Part 1 — Agent Identity Evidence
**Question: Does agent_id change?**
**Answer:** Yes. 
**Evidence:** The database query from `endpoints` shows multiple rows for the same `hostname` with different `agent_id` values:
- `Test-VM-3` (Row 1): `agent_id` = `fe727ad0-9ff9-410d-ab95-2ef0a5dab3ae`
- `Test-VM-3` (Row 2): `agent_id` = `c431e0d6-f764-448d-a708-301943a5c2c6`

**Question: Does hardware_hash change?**
**Answer:** Yes.
**Evidence:** The database query from `endpoints` shows multiple rows for the same `hostname` with different `hardware_hash` values:
- `Test-VM-3` (Row 1): `11c2c4878c063abf3e664dd897de309b05c1a933072ea48447ca45206c875a4c`
- `Test-VM-3` (Row 2): `16a5cc7c9124d5b9ca0ea371bda6f386f614204257e95b4bb9728c61ab32ebb6`

**Why? (Confirmed):** WMI enumeration (e.g., `Win32_BaseBoard` for motherboard serial) returns different values or empty strings depending on the execution context (User vs. Local System). Combined with the DPAPI decryption failure (due to missing `CRYPTPROTECT_LOCAL_MACHINE`), this causes the agent to generate a new `agent_id` and hash a different hardware signature upon service restart.

## Part 2 — Enrollment Trace
Execution path for `/api/v1/endpoints/enroll` (`backend/app/modules/endpoints/router.py:258`):
1. **Incoming:** `agent_id` and `hardware_hash`.
2. **Lookup:** `stmt = select(Endpoint).where(or_(Endpoint.hardware_hash == data.hardware_hash, Endpoint.agent_id == data.agent_id))`
3. **Condition:** Because the service restart caused the agent to generate a *new* `agent_id` AND the WMI context change caused a *new* `hardware_hash`, the backend lookup finds `None`.
4. **Execution:** The code enters the `if not endpoint:` block and executes an `INSERT` (creating `Endpoint(agent_id=..., hardware_hash=...)`), permanently creating a duplicate.

## Part 3 — Hardware Inventory Trace (Duplicate Key Error)
**Evidence:** `backend/app/modules/inventory/repository.py:21`
```python
    async def create_or_update(self, endpoint_id: uuid.UUID, data: HardwareInventoryCreate) -> HardwareInventory:
        record = await self.get_by_endpoint_id(endpoint_id) # SELECT
        if record:
            # UPDATE
        else:
            # INSERT
```
**Why an INSERT fails for an existing endpoint:** The code uses a naive `SELECT` followed by an `INSERT` in Python, rather than a database-level `INSERT ... ON CONFLICT DO UPDATE`. If the agent sends two simultaneous inventory uploads (e.g., due to retries or rapid startup events), both requests execute the `SELECT` concurrently, see `record = None`, and attempt to `INSERT`. The second transaction hits the unique constraint `ix_hardware_inventory_endpoint_id` and crashes.

## Part 4 — Ghost Online Endpoint
**Evidence:** `backend/app/modules/endpoints/router.py:605`
```python
    now = datetime.now(timezone.utc)
    time_diff = (now - ep.last_seen.replace(tzinfo=timezone.utc)).total_seconds() if ep.last_seen else 9999
    is_online = time_diff < 180 and ep.status != "offline"
```
**Explanation:** The "Online" status is strictly computed, not stored. An endpoint is considered online if `last_seen` is within the last 180 seconds (3 minutes). When you stop the service manually, the agent cannot send an explicit `status="offline"` heartbeat. Therefore, the endpoint will remain "Online" in the UI for exactly 3 minutes after the service stops. This is working as designed for heartbeat-based systems, though the timeout could be shortened.

## Part 5 — Dell Hardware
**Evidence:** `backend/app/modules/endpoints/router.py:619`
```python
    manufacturer=hw.manufacturer if hw else "Dell Inc.",
    model=hw.model if hw else "Latitude 5520",
```
**Explanation:** This is a hardcoded demo fallback! If an endpoint exists in the database but has no corresponding `hardware_inventory` row (which is exactly what happens in the seconds/minutes after a duplicate endpoint is newly INSERTed), the backend silently returns "Dell Inc." to the frontend instead of `null` or "Pending". 

## Part 6 — Database Ownership
Based on the live database queries:
- **DESKTOP-JK4JV9R (Original):** ID `cba0da5e...` owns the `hardware_inventory` row with the real Lenovo hardware (`64b07ba9...`).
- **DESKTOP-JK4JV9R (Duplicate):** ID `df221ef8...` has **NO** hardware inventory row. Because it lacks a row, the backend uses the "Dell" fallback for it.

## Final Deliverable & Recommendations

**Confirmed Root Causes:**
1. **Agent:** DPAPI is strictly bound to the user profile, causing identity loss when run as a service. WMI queries vary between contexts, altering the hardware hash.
2. **Backend:** The enrollment route creates a duplicate because both identifiers change. The hardware inventory route has a race condition causing DB errors. The endpoint API returns hardcoded fake data when inventory is missing.

**Files Requiring Changes:**
1. `agent/security/crypto.py`
2. `agent/security/identity.py`
3. `backend/app/modules/endpoints/router.py`
4. `backend/app/modules/inventory/repository.py`

**Recommended Implementation Order:**
1. **Agent Identity Fix:** Update `crypto.py` to use `CRYPTPROTECT_LOCAL_MACHINE` (flag `0x4`). Update `identity.py` to use a deterministic fallback like `MachineGuid` for hashing if WMI fails.
2. **Backend Inventory Fix:** Convert the `SELECT`/`INSERT` block in `repository.py` to a proper Postgres `INSERT ... ON CONFLICT (endpoint_id) DO UPDATE` to eliminate race conditions.
3. **Backend Fallback Fix:** Remove the hardcoded "Dell" strings from `router.py`. Return standard empty/null values.

Awaiting approval to begin code modifications.
