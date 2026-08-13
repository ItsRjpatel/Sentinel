# API DOCUMENTATION

## 1. Authentication
- **POST `/api/v1/auth/login`**: Authenticates admin and returns JWT.
- **POST `/api/v1/auth/refresh`**: Refreshes JWT access token.

## 2. Endpoints
- **GET `/api/v1/endpoints`**: Lists all enrolled endpoints (Admin only).
- **GET `/api/v1/endpoints/{id}`**: Retrieves specific endpoint metadata.
- **POST `/api/v1/endpoints/enroll`**: Registers a new agent. Requires shared enrollment secret.

## 3. Inventory
- **POST `/api/v1/inventory/hardware`**: Agent submits hardware specs.
- **POST `/api/v1/inventory/os`**: Agent submits OS details.
- **GET `/api/v1/inventory/{id}/hardware`**: Admin retrieves endpoint hardware.

## 4. Telemetry
- **POST `/api/v1/telemetry/heartbeat`**: Agent submits CPU/Memory usage. Returns pending commands.
- **GET `/api/v1/telemetry/{id}/metrics`**: Admin retrieves historical metrics.

## 5. Alerts
- **GET `/api/v1/alerts`**: Admin retrieves active/historical alerts.
- **POST `/api/v1/alerts/{id}/resolve`**: Admin manually resolves an alert.

## 6. Commands
- **POST `/api/v1/commands/queue`**: Admin queues a command for execution.
- **POST `/api/v1/commands/{id}/result`**: Agent submits execution stdout/stderr.
- **GET `/api/v1/commands/{id}`**: Admin retrieves command status.
