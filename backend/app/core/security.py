import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError

password_hash = PasswordHash((Argon2Hasher(),))


def get_password_hash(password: str) -> str:
    """Hashes a password using Argon2id."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an Argon2id hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | uuid.UUID,
    username: str,
    roles: List[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "token_type": "access",
        "sub": str(subject),
        "username": username,
        "roles": roles,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | uuid.UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates a JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "token_type": "refresh",
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def _decode_token(token: str, expected_type: str) -> Dict[str, Any]:
    """Internal helper to decode and validate a JWT token."""
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if decoded_token.get("token_type") != expected_type:
            raise InvalidTokenError(f"Invalid token type. Expected '{expected_type}'.")
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Token has expired.")
    except jwt.PyJWTError as e:
        raise InvalidTokenError(f"Invalid token: {e}")


def verify_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    return _decode_token(token, "access")


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT refresh token."""
    return _decode_token(token, "refresh")
