# Network and Real-Time Architecture

## Dynamic Endpoint Networking
The Sentinel Agent determines its network identity dynamically on every check-in, rather than solely at enrollment time.
This addresses scenarios where agents transition between physical LAN, Wi-Fi, and mobile hotspots, which natively changes their network addressing.

1. **Agent Telemetry Gathering**: The agent collects non-loopback active IP addresses from `socket.gethostbyname_ex` and transmits them within the heartbeat payload via the `ip_addresses` field.
2. **Backend Persistence**: The backend `POST /endpoints/heartbeat` route validates this array and directly patches `Endpoint.ip_addresses`. Endpoint identity continues to hinge securely on `agent_id` (a UUID assigned during enrollment, authenticated via short-lived JWTs derived from refresh tokens).

## Stateful Alerting & Offline Transitions
1. **Lightweight Evaluation Logic**: `EndpointAlertState` tracks the cumulative time constraints (e.g. `HIGH_MEMORY` exceeding `trigger_threshold` over `N` consecutive heartbeats).
2. **Offline Detection**: The backend flags agents as offline after missing 180 seconds of expected heartbeats. When an agent subsequently checks in, the offline -> online transition emits a one-time real-time event.

## WebSocket Broadcasting (Real-Time Engine)
Sentinel features a high-performance real-time engine built entirely on FastAPI WebSockets, negating the need for continuous REST polling from the UI.
1. **Decoupled Architecture**: 
   - **Agent -> Backend**: The agent remains stateless and exclusively uses standard REST HTTP methods (e.g., POST `/heartbeat`) for robust delivery across restrictive NATs and enterprise firewalls.
   - **Backend -> Frontend**: The backend leverages a central `ConnectionManager` to push real-time events to connected frontend operator clients over `ws://.../ws/notifications` and `ws://.../ws/commands`.
2. **Event Typology**:
   - `endpoint_online`: Emitted upon offline -> online transitions.
   - `performance_updated`: Dispatches lightweight CPU, RAM, and Disk metrics continuously for UI data visualization without heavy database retention.
   - `alert_created` / `alert_updated`: Notifies analysts of new incidents or lifecycle changes (e.g., resolutions/acknowledgements).
   - `notification_created`: Refreshes the top-right notification bell and unread counts instantly.
3. **Frontend Integration**: The React frontend wraps standard API hooks within a `GlobalWebSocketProvider` to ingest updates without redefining the React-Query or Axios data layers.
