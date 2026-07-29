import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

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

    # Required M1.3 Payload fields
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


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_token
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid token: {e}")
