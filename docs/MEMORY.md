# Memory
## Project Context
- **Name**: Sentinel
- **Goal**: Build a scalable, agent-based Endpoint Management System.
- **Rules**: Documentation First Development, backend owns business logic, architecture is frozen.

## Technical Decisions
- Python 3.13+, FastAPI, Uvicorn, SQLAlchemy 2.x Async, Alembic.
- PostgreSQL (Neon Database).
- Architecture: Vertical Slice (Feature-First) architecture using Domain-Driven Design principles (`backend/app/modules/`).

## Current State
- **Sprint 1.1 Complete**: Code quality suite verified; global `.venv` and `pyproject.toml` established.
- **Milestone M0.4 Complete**: Foundation Freeze applied. CI pipelines, docker skeletons, and developer config standardizations complete.
- **Milestone M0.5 Complete**: Architecture Migration from Layered to Feature-First. `app/modules/` created, and `app/common/` established.
- **Milestone M1.1 Complete**: Identity & Access Database Models (`User`, `Role`, `Permission`, `RefreshToken`) designed with Pydantic Schemas. Soft delete and UUID mixins successfully added to `app/common/models.py`. Validated via unit tests.
- **Milestone M1.1A Complete**: Authentication Domain Architectural Review completed.
- **Milestone M1.2 Complete**: Authentication Repository Layer (`UserRepository`, `RoleRepository`, `PermissionRepository`, `RefreshTokenRepository`) implemented. Extracted SQLAlchemy exception mapping into `auth.exceptions`.

## Next Steps
- Wait for user instruction to begin Milestone M1.3 (Service Layer).