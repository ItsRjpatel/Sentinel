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
- **Milestone M1.3 Complete**: Authentication Service Layer (`AuthenticationService`, `pwdlib`, `PyJWT`) implemented to bridge the gap between HTTP APIs and Database logic.
- **Pre-M1.4 Consistency Complete**: Added `failed_login_attempts`, `locked_until`, `last_failed_login` to `User` model. Generated migration `5278bf03f271`.
- **Milestone M1.4 Complete**: Dependency Injection Layer. Implemented `get_db()`, `get_auth_service()`, and repository providers in `dependencies.py`.
- **Milestone M1.5A & M1.5B Complete**: Authentication API Specification and Router Implementation. Mapped all 15 API endpoints with standard response structures and exception handlers.
- **Milestone M1.5.1 Complete**: Validation Review. Successfully validated 100% of endpoints against API specification. Test suite verified passing.

## Next Steps
- Wait for user instruction to begin Milestone M1.6 (JWT Authorization Middleware).