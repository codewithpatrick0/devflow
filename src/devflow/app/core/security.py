from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from devflow.app.core.config import settings

ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'

# recommended() pins argon2id with the parameters pwdlib currently considers
# safe, so the cost can be raised later by upgrading the library.
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hasher.verify(password, hashed)


def _secret_for(token_type: str) -> str:
    if token_type == ACCESS_TOKEN_TYPE:
        return settings.secret_key

    if token_type == REFRESH_TOKEN_TYPE:
        return settings.refresh_secret_key

    # Never fall back to a key: an unknown type is a bug, and defaulting here
    # would sign the token with the wrong secret instead of saying so.
    raise ValueError(f'unknown token type: {token_type}')


def create_token(subject: str, token_type: str, expires_in: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': subject,
        'type': token_type,
        'iat': now,
        'exp': now + expires_in,
    }
    return jwt.encode(
        payload,
        _secret_for(token_type),
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(subject: str) -> str:
    return create_token(
        subject,
        ACCESS_TOKEN_TYPE,
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject,
        REFRESH_TOKEN_TYPE,
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    # The algorithm comes from our settings, never from the token header:
    # trusting the header is what enables algorithm confusion attacks.
    payload = jwt.decode(
        token,
        _secret_for(expected_type),
        algorithms=[settings.jwt_algorithm],
    )

    # Redundant with the separate secrets, and kept on purpose: the signature
    # stops a forged token, this makes the failure say what actually happened.
    if payload.get('type') != expected_type:
        raise jwt.InvalidTokenError(f'expected a {expected_type} token')

    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, ACCESS_TOKEN_TYPE)


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, REFRESH_TOKEN_TYPE)
