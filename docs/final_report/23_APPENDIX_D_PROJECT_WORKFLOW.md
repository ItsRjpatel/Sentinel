# APPENDIX D: PROJECT WORKFLOW

## Endpoint Enrollment Workflow
1. Administrator launches SentinelAgent.exe GUI.
2. User inputs Server URL and Secret Token.
3. Agent generates hardware fingerprint and UUID.
4. Agent sends POST /endpoints/enroll.
5. Server validates token, stores endpoint, returns JWTs.
6. Agent stores JWTs securely via DPAPI.
7. Agent installs itself as a Windows Service and starts.

## Telemetry Workflow
1. HeartbeatTask awakes every X seconds.
2. Extracts CPU & Memory via psutil.
3. POSTs payload to /telemetry/heartbeat with JWT.
4. Server validates JWT, updates endpoint last_seen.
5. Server persists telemetry in the database.
6. Server passes payload to AlertService.

## Alert Workflow
1. AlertService evaluates CPU/Memory against thresholds (e.g., >90%).
2. If threshold exceeded over consecutive samples, check EndpointAlertState.
3. If no active alert exists, create Alert and Notification.
4. Broadcast WebSocket event to all connected UI clients.
5. If threshold drops below safe limit, resolve alert and update state.
