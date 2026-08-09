# Enterprise Investigation Report: Duplicate Endpoint & Incorrect Hardware Bug

## 1. Investigation of Enrollment
**What uniquely identifies an endpoint?**
The Sentinel Agent uses a `hardware_hash` (a SHA-256 hash of the `bios_uuid`, `cpu_id`, and `motherboard_serial`) and a logical `agent_id` (a generated UUID). 

During enrollment (`/api/v1/endpoints/enroll`), the backend searches for an existing endpoint using:
```python
stmt = select(Endpoint).where(
    or_(
        Endpoint.hardware_hash == data.hardware_hash,
        Endpoint.agent_id == data.agent_id
    )
)
```
If neither the `hardware_hash` nor the `agent_id` match an existing record, the backend generates a completely new endpoint record.

## 2. Check if Enrollment Always INSERTs
The backend **does not** always `INSERT`. It attempts to find and update an existing endpoint.
However, because both `hardware_hash` and `agent_id` change under specific conditions (service restart), the `WHERE` clause fails to find the existing endpoint, forcing the backend into the `INSERT` block.

## 3. Investigation of Agent Identity
The agent's identity is defined in `agent/security/identity.py`. 
The identity lifecycle relies on `identity.json`, which stores the `agent_uuid` and `machine_fingerprint`. 
This file is encrypted using Windows DPAPI (`agent/security/crypto.py`).

## 4. Database Investigation
A query against the `endpoints` table revealed that identical machines (`DESKTOP-JA3N7RS`, `DESKTOP-JK4JV9R`, `Test-VM-3`) have multiple active `endpoint_id` rows.
Crucially, the `hardware_hash` value is different for the duplicates, even though they represent the same physical machine. 

## 5. Verify Every JOIN
An inspection of `backend/app/modules/endpoints/router.py` shows that all APIs (Overview, Hardware, Storage, etc.) correctly query using `WHERE endpoint_id = ep.id`. The backend does not incorrectly join by `hostname`. The issue is not with the SQL JOINs; it is with the existence of multiple unique endpoint UUIDs for the same machine.

## 6. Search for Demo or Seed Data
A search across the backend for "Dell" revealed the exact cause of the incorrect hardware bug.
In `router.py`, the `get_hardware` and `get_overview` functions use hardcoded fallback demo data if the database returns `None` for a relation:
```python
manufacturer=hw.manufacturer if hw else "Dell Inc.",
model=hw.model if hw else "Latitude 5520",
```
When a duplicate endpoint is newly created by the enrollment process, it has no associated hardware inventory records yet. When the frontend immediately queries the endpoint details, the backend silently falls back to returning the hardcoded "Dell" mock data.

## 7. Agent Investigation
Why does the agent generate a new `agent_id` and `hardware_hash`?
1. **DPAPI Context Failure:** The `identity.json` file is encrypted using DPAPI `CryptProtectData` without specifying the `CRYPTPROTECT_LOCAL_MACHINE` flag. DPAPI encrypts this file relative to the *current user*. If the agent is run manually during setup (e.g., as `Administrator`), it is encrypted with the user's master key. When the Windows Service later restarts as `Local System`, DPAPI cannot decrypt the file. The agent silently catches this exception and treats the machine as unenrolled, generating a new `agent_id`.
2. **WMI Privilege Discrepancy:** The `hardware_hash` is built from WMI queries (`Win32_ComputerSystemProduct`, `Win32_BaseBoard`). `Local System` has different WMI enumeration privileges than standard or admin users. The WMI query for the motherboard serial number returns different results (or empty strings) depending on the execution context. This alters the raw signature, resulting in a completely different SHA-256 `hardware_hash`.

## 8. Enterprise Review
The current architecture violates enterprise EDR expected behavior:
- A single physical endpoint must maintain a single identity forever.
- Identity should not rely on user-specific DPAPI encryption.
- The backend must never return hardcoded "Dell" mock data if an endpoint's inventory is simply empty.

## 9. Root Cause Report
**Exact Root Cause:** 
1. **Agent Issue:** DPAPI encryption context mismatch between the user who installed/ran the agent and the `Local System` account running the service causes identity loss. WMI context differences cause the `hardware_hash` to change.
2. **Backend Issue:** The backend fails to recognize the machine because both identifiers change, resulting in a duplicate `INSERT`. The backend then returns hardcoded mock data ("Dell") for endpoints lacking an inventory record.

**Files Responsible:**
- `agent/utils/storage.py` (DPAPI encryption implementation)
- `agent/security/crypto.py` (Missing `CRYPTPROTECT_LOCAL_MACHINE` flag)
- `agent/security/identity.py` (WMI hardware hash generation differences)
- `backend/app/modules/endpoints/router.py` (Hardcoded Dell fallbacks)

**Recommended Enterprise-Grade Fix:**
1. **Agent Crypto:** Modify DPAPI calls in `crypto.py` to use `CRYPTPROTECT_LOCAL_MACHINE` so the identity file is tied to the physical machine, not the user profile.
2. **Hardware Fingerprint:** Standardize the WMI queries or rely exclusively on `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` to ensure the `hardware_hash` is 100% deterministic across all system accounts.
3. **Backend Fallbacks:** Remove all hardcoded "Dell" and demo data from `router.py`. If an inventory record does not exist, the API should return `null` or "Pending", and the frontend should display "Waiting for telemetry...".
