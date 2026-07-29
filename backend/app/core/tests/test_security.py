import uuid
from datetime import timedelta

import pytest

from app.core.exceptions import ExpiredTokenError, InvalidTokenError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


def test_create_and_verify_access_token():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "admin", ["admin"])
    payload = verify_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["username"] == "admin"
    assert payload["roles"] == ["admin"]
    assert payload["token_type"] == "access"


def test_create_and_verify_refresh_token():
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)
    payload = verify_refresh_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["token_type"] == "refresh"
    assert "username" not in payload


def test_verify_access_token_wrong_type():
    user_id = uuid.uuid4()
    # Create refresh token, but try to verify as access token
    token = create_refresh_token(user_id)
    with pytest.raises(InvalidTokenError, match="Invalid token type"):
        verify_access_token(token)


def test_verify_refresh_token_wrong_type():
    user_id = uuid.uuid4()
    # Create access token, but try to verify as refresh token
    token = create_access_token(user_id, "admin", [])
    with pytest.raises(InvalidTokenError, match="Invalid token type"):
        verify_refresh_token(token)


def test_expired_token():
    user_id = uuid.uuid4()
    token = create_access_token(
        user_id, "admin", [], expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(ExpiredTokenError, match="Token has expired"):
        verify_access_token(token)


def test_invalid_signature():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "admin", [])
    # Tamper with the token signature
    parts = token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.invalid_signature"
    with pytest.raises(InvalidTokenError, match="Invalid token"):
        verify_access_token(tampered_token)
