# Technology Stack

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | Technology Stack |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the approved technology stack for Sentinel.

Every contributor and AI coding assistant must use the technologies listed in this document.

Introducing new frameworks or libraries requires architectural review.

---

# 2. Architecture

| Layer | Technology |
|--------|------------|
| Architecture | Layered / Clean Architecture |
| API Style | REST + WebSockets |
| Communication | JSON |
| Authentication | JWT |
| Authorization | Role-Based Access Control (RBAC) |

---

# 3. Backend

| Component | Technology |
|------------|------------|
| Language | Python 3.13+ |
| Framework | FastAPI |
| ASGI Server | Uvicorn |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x Async |
| Database Driver | asyncpg |
| Database Migrations | Alembic |

---

# 4. Database

| Component | Technology |
|------------|------------|
| Cloud Database | Neon PostgreSQL |
| Database Engine | PostgreSQL 17+ |
| Connection Pooling | Neon Pooler |
| SSL | Required |

---

# 5. Frontend

The web application follows a server-rendered architecture.

| Component | Technology |
|------------|------------|
| HTML | HTML5 |
| Styling | CSS3 |
| UI Framework | Bootstrap 5 |
| JavaScript | Vanilla JavaScript (ES6+) |
| Template Engine | Jinja2 |
| Charts | Chart.js |
| Icons | Bootstrap Icons |

No React, Angular, Vue, Svelte, or other SPA frameworks are used in Version 1.

---

# 6. Windows Agent

| Component | Technology |
|------------|------------|
| Language | Python 3.13+ |
| Type | Windows Service |
| Windows APIs | WMI / CIM / PowerShell / Native APIs |
| HTTP Client | httpx |
| WebSocket Client | websockets |

---

# 7. Security

| Component | Technology |
|------------|------------|
| Authentication | JWT |
| Password Hashing | Argon2 |
| Transport Security | HTTPS + TLS |
| Secrets | Environment Variables |
| Database Connection | SSL |

---

# 8. Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version Control |
| GitHub | Repository Hosting |
| VS Code | Primary IDE |
| Cursor | AI Development |
| Claude | AI Development |
| Antigravity | AI Development |
| ChatGPT | Architecture, Planning, Review |

---

# 9. Testing

| Component | Technology |
|------------|------------|
| Unit Testing | Pytest |
| API Testing | Pytest + HTTPX |
| Integration Testing | Pytest |
| Coverage | pytest-cov |

---

# 10. Code Quality

| Tool | Purpose |
|------|---------|
| Ruff | Linting |
| Black | Formatting |
| isort | Import Sorting |
| mypy | Static Type Checking |

---

# 11. Deployment

| Component | Technology |
|------------|------------|
| Containerization | Docker |
| Reverse Proxy | Nginx |
| Process Manager | systemd (Linux) |
| Environment | .env Files |

---

# 12. Logging

Logging Requirements

- Structured logging
- UTC timestamps
- Request IDs
- Security event logging
- Error logging
- Audit logging

Sensitive information must never be written to logs.

---

# 13. Configuration

Configuration must come from environment variables.

Examples

```env
DATABASE_URL=
SECRET_KEY=
JWT_SECRET_KEY=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

No secrets may be hardcoded.

---

# 14. API Standards

- JSON only
- RESTful endpoints
- Versioned APIs (`/api/v1`)
- WebSockets for real-time communication
- UTF-8 encoding
- Consistent response format

---

# 15. AI Development Rules

All AI coding assistants must follow these rules:

- Use only approved libraries.
- Do not introduce additional frameworks.
- Do not change project architecture.
- Do not replace approved technologies.
- Follow existing folder structure.
- Generate production-quality code.
- Add type hints where applicable.
- Write clear docstrings for public functions.

---

# 16. Technology Decisions

| Category | Decision |
|----------|----------|
| Backend | FastAPI |
| Database | Neon PostgreSQL |
| ORM | SQLAlchemy Async |
| Driver | asyncpg |
| Migration | Alembic |
| Frontend | HTML + Bootstrap + Jinja2 + Vanilla JavaScript |
| Agent | Python Windows Service |
| Charts | Chart.js |
| Authentication | JWT |
| Authorization | RBAC |
| Testing | Pytest |
| Formatting | Black |
| Linting | Ruff |
| Type Checking | mypy |
| Deployment | Docker |

---

# 17. Prohibited Technologies

The following are not part of Version 1 unless explicitly approved:

- React
- Angular
- Vue
- Svelte
- Django
- Flask
- SQLite
- MySQL
- MongoDB
- Celery
- Redis (unless added through an Architecture Decision Record)
- GraphQL

---

# 18. Future Considerations

The architecture allows future adoption of:

- Redis (Caching / Pub/Sub)
- RabbitMQ
- Elasticsearch
- OpenSearch
- Prometheus
- Grafana
- Kubernetes
- OpenTelemetry

These technologies will only be introduced when a clear business or scalability need exists.

---

# 19. Summary

Sentinel follows a modern, cloud-native technology stack centered on FastAPI, Neon PostgreSQL, SQLAlchemy Async, and a lightweight server-rendered web interface.

This standardized stack ensures consistency, maintainability, and compatibility across all AI development tools while providing a solid foundation for enterprise-scale endpoint management.