from app.core.exceptions import AuthenticationError


class RepositoryError(Exception):
    """Base exception for all repository errors."""

    pass


class IntegrityError(RepositoryError):
    """Raised when a database integrity constraint is violated."""

    pass


class DuplicateEntryError(RepositoryError):
    """Raised when an entity violates a unique constraint."""

    pass


class NotFoundError(RepositoryError):
    """Raised when an entity is not found in the database."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login fails due to bad credentials."""

    pass


class UnauthorizedError(AuthenticationError):
    """Raised when a user attempts an action without authorization."""

    pass
