# Changelog

## [Unreleased]
### Added
- **M1.3 Auth Service**:
  - Replaced `passlib` with `pwdlib` and `argon2-cffi`.
  - Added `PyJWT` for JWT generation/validation.
  - Implemented `AuthenticationService` logic and integration tests.
- **M1.2 Auth Repositories**:
  - Implemented `UserRepository`, `RoleRepository`, `PermissionRepository`, `RefreshTokenRepository`.
  - Added custom `RepositoryError`, `NotFoundError`, `DuplicateEntryError`, `IntegrityError`.
- **M1.1 Identity & Access**:
  - Implemented `User`, `Role`, `Permission`, `RefreshToken` SQLAlchemy models.
  - Implemented `BaseModelMixin` with UUID, audit fields, and soft deletion.
  - Implemented Authentication Pydantic schemas in `modules/auth/schemas.py`.
### Changed
- **M0.5 Architecture Migration**:
  - Migrated backend from horizontal layered structure to vertical Feature-First (Slice) architecture.
  - Moved endpoints into `app/modules/monitoring/router.py`.
  - Moved infrastructure into `app/common/middleware/`.
  - Deleted obsolete empty layered directories (`models`, `schemas`, `services`, etc.).
  - Updated project documentation to reflect `modules/` based architecture.
### Added
- **M0.4 Foundation Freeze**:
  - `web/`, `agent/`, `infrastructure/`, `tests/`, `tools/`, `scripts/` directories to match architectural documentation.
  - GitHub Actions for backend CI, linting, and testing (`.github/workflows/`).
  - VS Code configurations for Python linting, debugging, and testing (`.vscode/`).
  - Core Git files (`.gitignore`, `.gitattributes`).
  - Editor configuration (`.editorconfig`).
  - Developer automation scripts for Windows (`.ps1`) and Linux (`.sh`) in `scripts/`.
  - Docker skeleton (`Dockerfile`, `docker-compose.yml`, `.dockerignore`) in root.
  - Pre-commit configurations (`.pre-commit-config.yaml`).
  - MIT License (`LICENSE`).
### Changed
- Moved and unified backend `.gitignore` to the project root.
- Renamed `Docs/` to `docs/`.

## [0.1.0-alpha.1] - Sprint 1.1 Completion
### Changed
- Migrated dependency management strictly to `pyproject.toml`.
- Unified virtual environment to repository root (`.venv`).
- Corrected type errors in backend to pass `mypy --strict`.

## [0.1.0-alpha] - Sprint 1 Completion
### Added
- Initial backend setup using FastAPI, SQLAlchemy Async, and Alembic.
- Code quality toolset: ruff, black, isort, mypy, pytest.
- Global Pydantic settings loading.
- Middleware structure and Logging handlers.
