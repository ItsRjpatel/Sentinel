class RepositoryError(Exception):
    """Base exception for all repository errors."""
    pass


class NotFoundError(RepositoryError):
    """Raised when an entity is not found in the database."""
    pass


class DuplicateEntryError(RepositoryError):
    """Raised when an entity violates a unique constraint."""
    pass


class IntegrityError(RepositoryError):
    """Raised when a database integrity constraint is violated."""
    pass
