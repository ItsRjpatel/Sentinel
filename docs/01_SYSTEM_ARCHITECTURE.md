# System Architecture

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | System Architecture |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the overall system architecture of Sentinel.

It describes how the platform components communicate, where responsibilities belong, and the architectural principles that guide development.

This document serves as the primary technical reference for all implementation work.

---

# 2. Architecture Overview

Sentinel follows a modular client-server architecture.

The platform consists of four major components:

1. Web Application
2. Backend API
3. Windows Agent
4. PostgreSQL Database

Each component has clearly defined responsibilities and communicates through secure interfaces.

---

# 3. High-Level Architecture

                    +----------------------+
                    |      Administrator   |
                    +----------+-----------+
                               |
                               |
                               v
                  +---------------------------+
                  |      Web Application      |
                  | HTML • CSS • JavaScript   |
                  +------------+--------------+
                               |
                     HTTPS (REST API)
                               |
                               v
                 +-----------------------------+
                 |      FastAPI Backend        |
                 | Authentication              |
                 | Business Logic              |
                 | WebSocket Manager           |
                 | API Layer                   |
                 +------+----------------------+
                        |
        +---------------+----------------+
        |                                |
        |                                |
        v                                v
+-------------------+           +----------------------+
| PostgreSQL        |           | WebSocket Clients    |
| Primary Database  |           | Live Dashboard       |
+-------------------+           +----------------------+
        ^
        |
        |
 HTTPS + WebSocket
        |
        v
+---------------------------+
| Windows Agent             |
| Inventory                 |
| Monitoring                |
| Compliance                |
| Remote Commands           |
+---------------------------+

---

# 4. Major Components

## 4.1 Web Application

Responsibilities

- User Interface
- Dashboard
- Reports
- Device Management
- Authentication
- Live Monitoring
- Settings

The frontend does not contain business logic.

Its responsibility is presenting data returned by the backend.

---

## 4.2 Backend API

The backend is the core of the platform.

Responsibilities

- Authentication
- Authorization
- Business Rules
- Validation
- Inventory Processing
- Monitoring Engine
- Compliance Engine
- Alert Engine
- Reporting
- Audit Logging
- WebSocket Communication

All business logic resides here.

---

## 4.3 Windows Agent

Installed on managed endpoints.

Responsibilities

- Device Enrollment
- Hardware Inventory
- Software Inventory
- Performance Monitoring
- Security Information
- Compliance Data
- Execute Remote Commands
- Heartbeat

The agent never communicates directly with the database.

---

## 4.4 Database

Stores all persistent information.

Examples

- Users
- Roles
- Endpoints
- Inventory
- Alerts
- Reports
- Audit Logs
- Security Status
- Compliance Results

---

# 5. Communication Flow

## User Request

Administrator

↓

Web Application

↓

REST API

↓

Backend

↓

Database

↓

Response

↓

Web Application

---

## Live Monitoring

Windows Agent

↓

WebSocket

↓

Backend

↓

Web Application

---

## Inventory Collection

Windows Agent

↓

REST API

↓

Backend Validation

↓

Database

---

## Remote Command

Administrator

↓

Backend

↓

WebSocket

↓

Windows Agent

↓

Execution Result

↓

Backend

↓

Dashboard

---

# 6. Communication Protocols

## REST API

Purpose

- Authentication
- CRUD Operations
- Inventory Upload
- Reports
- Configuration

Characteristics

- Stateless
- HTTPS Only
- JSON
- JWT Authentication

---

## WebSocket

Purpose

- Live Dashboard
- Alerts
- Endpoint Status
- Remote Command Execution
- Notifications

Characteristics

- Persistent Connection
- Event Driven
- Authenticated
- Low Latency

---

# 7. Architectural Principles

## Separation of Concerns

Every module has a single responsibility.

---

## Backend-Centric Design

Business logic exists only in the backend.

The frontend is responsible only for presentation.

---

## Modular Design

Each module can evolve independently.

Examples

- Inventory
- Monitoring
- Security
- Alerts

---

## API-First Development

Every feature begins with API design.

Frontend and agent consume the same APIs.

---

## Security by Design

Every request is authenticated.

Every action is authorized.

Every important event is audited.

---

## Scalability

The platform must support thousands of endpoints.

Scaling should require infrastructure changes rather than architectural redesign.

---

# 8. System Modules

Core platform modules include:

- Identity & Access
- Endpoint Management
- Inventory
- Monitoring
- Security
- Compliance
- Vulnerability Assessment
- Remote Management
- Alerts
- Reports
- Audit Logs
- Settings

Each module is designed to be independent while integrating through shared backend services.

---

# 9. Data Ownership

| Component | Owns Data |
|------------|-----------|
| Web Application | No |
| Backend | Yes |
| Agent | Temporary |
| Database | Persistent |

The backend is the only component permitted to modify persistent data.

---

# 10. Error Handling Strategy

Validation errors are handled in the backend.

Unexpected exceptions are logged.

Sensitive information is never exposed to clients.

Audit records are created for security-relevant operations.

---

# 11. Security Model

Authentication

↓

Authorization

↓

Business Validation

↓

Database Access

↓

Audit Logging

Every protected request passes through these layers.

---

# 12. Future Expansion

The architecture supports future additions without redesign.

Potential future modules include:

- Patch Management
- Software Deployment
- Remote Desktop
- Linux Agent
- macOS Agent
- Multi-Tenant Support
- AI Assistant
- High Availability
- Distributed Processing

---

# 13. Architecture Summary

Sentinel follows a modular, backend-centric architecture that separates presentation, business logic, endpoint operations, and persistent storage.

The architecture emphasizes security, scalability, maintainability, and extensibility while ensuring that all critical business logic remains centralized within the backend.