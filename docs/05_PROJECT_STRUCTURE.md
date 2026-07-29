# Project Structure

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | Project Structure |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the official repository structure for Sentinel.

Every source file, configuration file, documentation file, test, and deployment artifact must follow this structure.

No new top-level folders should be introduced without architectural review.

---

# 2. Repository Structure

```
Sentinel/
│
├── backend/                 # FastAPI Backend
├── web/                     # HTML/CSS/JavaScript Web Application
├── agent/                   # Windows Agent
├── docs/                    # Project Documentation
├── infrastructure/          # Deployment & Infrastructure
├── tests/                   # Integration & End-to-End Tests
├── tools/                   # Development Utilities
├── scripts/                 # Helper Scripts
│
├── .editorconfig
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── CHANGELOG.md
```

---

# 3. Backend Structure

```
backend/
│
├── app/
│   ├── core/
│   ├── db/
│   ├── common/
│   │   └── middleware/
│   ├── modules/
│   │   ├── auth/
│   │   ├── endpoints/
│   │   ├── inventory/
│   │   ├── monitoring/
│   │   ├── security/
│   │   ├── compliance/
│   │   ├── commands/
│   │   ├── alerts/
│   │   ├── reports/
│   │   ├── audit/
│   │   └── settings/
│   └── main.py
│
├── alembic/
├── tests/
│
├── requirements.txt
└── pyproject.toml
```

---

# 4. Web Structure

```
web/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── img/
│   └── fonts/
│
├── templates/
│
├── pages/
│
└── assets/
```

---

# 5. Windows Agent Structure

```
agent/
│
├── collectors/
├── commands/
├── communication/
├── security/
├── scheduler/
├── services/
├── utils/
│
├── config.py
├── main.py
└── requirements.txt
```

---

# 6. Documentation Structure

```
docs/
│
├── 00_PROJECT_OVERVIEW.md
├── 01_SYSTEM_ARCHITECTURE.md
├── 02_DATABASE_DESIGN.md
├── 03_API_SPECIFICATION.md
├── 04_DEVELOPMENT_PLAN.md
├── 05_PROJECT_STRUCTURE.md
├── 06_TECH_STACK.md
├── 07_AI_DEVELOPMENT_WORKFLOW.md
├── 08_CODING_STANDARDS.md
├── ADR/
└── diagrams/
```

---

# 7. Infrastructure

```
infrastructure/
│
├── docker/
├── nginx/
├── github/
├── deployment/
└── monitoring/
```

---

# 8. Test Structure

```
tests/
│
├── api/
├── integration/
├── performance/
├── security/
├── agent/
└── web/
```

---

# 9. Scripts

```
scripts/
│
├── setup/
├── database/
├── deployment/
└── maintenance/
```

---

# 10. Module Organization

Backend modules are organized by business capability.

```
Authentication

Endpoint Management

Inventory

Monitoring

Security

Compliance

Remote Commands

Alerts

Reports

Audit
```

Every module contains:

- router.py
- service.py
- repository.py
- models.py
- schemas.py
- dependencies.py
- __init__.py

---

# 11. File Naming Standards

Python

```
snake_case.py
```

HTML

```
lowercase.html
```

JavaScript

```
snake_case.js
```

CSS

```
snake_case.css
```

Documentation

```
UPPERCASE_NAME.md
```

---

# 12. Import Rules

Allowed

```
API

↓

Services

↓

Repositories

↓

Database
```

Forbidden

```
Repository

↓

API
```

Business logic must never exist inside routes.

---

# 13. Dependency Direction

```
Web

↓

API

↓

Service

↓

Repository

↓

Database
```

The flow is one-directional.

---

# 14. Growth Policy

New modules should be added without restructuring existing folders.

Examples:

- Patch Management
- Software Deployment
- Linux Agent
- macOS Agent
- Mobile API

must fit naturally into the existing layout.

---

# 15. Repository Rules

- No unnecessary folders.
- One responsibility per folder.
- Keep modules independent.
- Avoid circular dependencies.
- Documentation evolves with architecture.
- Tests mirror the production structure.

---

# 16. Summary

The Sentinel repository is organized around business domains and clear separation of responsibilities.

The structure is designed to support long-term maintainability, parallel development, and enterprise-scale growth while keeping the codebase easy to navigate for both developers and AI coding assistants.
