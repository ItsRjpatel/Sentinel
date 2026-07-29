# API Specification

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | API Specification |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the API standards used throughout Sentinel.

It specifies:

- API conventions
- Authentication
- Request format
- Response format
- Error handling
- REST endpoints
- WebSocket events
- Versioning strategy

The API serves as the communication layer between:

- Web Application
- Windows Agent
- Backend Services

---

# 2. API Design Principles

Sentinel follows RESTful API principles.

Design goals:

- Predictable
- Consistent
- Secure
- Versioned
- Stateless
- JSON-based
- Easy to consume

---

# 3. Base URL

Development

```

http://localhost:8000/api/v1

```

Production

```

https://api.company.com/api/v1

```

---

# 4. API Versioning

Every endpoint belongs to a version.

Example

```

/api/v1/

```

Future versions

```

/api/v2/

```

Older versions remain supported according to the product lifecycle policy.

---

# 5. Content Type

Request

```

Content-Type: application/json

```

Response

```

application/json

```

---

# 6. Authentication

Authentication uses JWT Bearer Tokens.

Example

```

Authorization: Bearer <access_token>

```

All protected endpoints require authentication.

Public endpoints are explicitly documented.

---

# 7. Standard Response Format

Every successful response follows:

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

---

Every error response follows:

```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": []
}
```

---

# 8. HTTP Status Codes

| Code | Meaning |
|-------|----------|
|200|OK|
|201|Created|
|204|No Content|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|500|Internal Server Error|

---

# 9. Authentication APIs

POST

```
/auth/login
```

POST

```
/auth/logout
```

POST

```
/auth/refresh
```

GET

```
/auth/me
```

POST

```
/auth/change-password
```

---

# 10. User APIs

GET

```
/users
```

GET

```
/users/{id}
```

POST

```
/users
```

PUT

```
/users/{id}
```

DELETE

```
/users/{id}
```

---

# 11. Role APIs

GET

```
/roles
```

POST

```
/roles
```

PUT

```
/roles/{id}
```

DELETE

```
/roles/{id}
```

---

# 12. Endpoint APIs

GET

```
/endpoints
```

GET

```
/endpoints/{id}
```

POST

```
/endpoints/enroll
```

POST

```
/endpoints/heartbeat
```

PUT

```
/endpoints/{id}
```

DELETE

```
/endpoints/{id}
```

---

# 13. Inventory APIs

GET

```
/inventory/{endpoint_id}
```

POST

```
/inventory/upload
```

GET

```
/inventory/hardware
```

GET

```
/inventory/software
```

GET

```
/inventory/network
```

GET

```
/inventory/storage
```

---

# 14. Monitoring APIs

GET

```
/monitoring/live
```

GET

```
/monitoring/history
```

POST

```
/monitoring/upload
```

---

# 15. Security APIs

GET

```
/security/{endpoint_id}
```

POST

```
/security/upload
```

---

# 16. Compliance APIs

GET

```
/compliance/{endpoint_id}
```

POST

```
/compliance/evaluate
```

GET

```
/compliance/history
```

---

# 17. Vulnerability APIs

GET

```
/vulnerabilities
```

GET

```
/vulnerabilities/{endpoint_id}
```

---

# 18. Remote Command APIs

POST

```
/commands
```

GET

```
/commands
```

GET

```
/commands/{id}
```

DELETE

```
/commands/{id}
```

---

# 19. Alert APIs

GET

```
/alerts
```

GET

```
/alerts/{id}
```

PUT

```
/alerts/{id}
```

DELETE

```
/alerts/{id}
```

---

# 20. Report APIs

GET

```
/reports
```

POST

```
/reports/generate
```

GET

```
/reports/download/{id}
```

---

# 21. Audit APIs

GET

```
/audit
```

GET

```
/audit/{id}
```

---

# 22. Settings APIs

GET

```
/settings
```

PUT

```
/settings
```

---

# 23. Agent APIs

POST

```
/agent/enroll
```

POST

```
/agent/heartbeat
```

POST

```
/agent/inventory
```

POST

```
/agent/monitoring
```

POST

```
/agent/security
```

POST

```
/agent/compliance
```

GET

```
/agent/commands
```

POST

```
/agent/commands/result
```

---

# 24. WebSocket API

Connection

```
ws://server/api/v1/ws
```

Authenticated WebSocket connection required.

---

## Events

### Endpoint

```
endpoint.online

endpoint.offline
```

---

### Monitoring

```
monitoring.updated

performance.updated
```

---

### Alerts

```
alert.created

alert.updated

alert.resolved
```

---

### Commands

```
command.created

command.started

command.completed

command.failed
```

---

### Notifications

```
notification.created
```

---

# 25. Pagination

Collection endpoints support pagination.

Example

```
GET /endpoints?page=1&page_size=50
```

---

# 26. Filtering

Example

```
GET /endpoints?status=online
```

---

# 27. Sorting

Example

```
GET /endpoints?sort=hostname
```

---

# 28. Searching

Example

```
GET /endpoints?search=laptop
```

---

# 29. API Security

Every protected request must:

- Use HTTPS
- Include JWT
- Pass RBAC validation
- Be logged if security-sensitive

---

# 30. Rate Limiting

Future implementation:

- Login protection
- Agent upload throttling
- API abuse prevention

---

# 31. Logging

Every request logs:

- User
- Endpoint
- IP
- Timestamp
- Status Code
- Execution Time

Sensitive data is never logged.

---

# 32. API Standards

Rules:

- JSON only
- Stateless
- Versioned
- Predictable URLs
- Resource-oriented
- Proper HTTP methods
- Consistent response format

---

# 33. Future APIs

Reserved for future modules:

- Patch Management
- Software Deployment
- License Management
- Remote Desktop
- CVE Integration
- AI Assistant
- Mobile API

---

# 34. Summary

The Sentinel API is designed as a versioned, secure, REST-first interface with WebSocket support for real-time communication.

It provides a consistent contract between the Web Application, Windows Agent, and Backend while remaining extensible for future enterprise features.