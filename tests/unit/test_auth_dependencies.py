from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from devflow.app.core.security import create_access_token, create_refresh_token
from devflow.app.dependencies.auth import (
    get_current_user_from_access_token,
    get_current_user_from_refresh_token,
)
from devflow.app.models import User


@pytest.fixture
def mock_user() -> User:
    return User(
        id=9,
        email='patrick@example.com',
        username='patrick',
        password_hash='not-used-in-this-test',
    )


#Small function by dependency
def make_request(cookie_name: str, token: str) -> Request:
    return Request({
        'type': 'http',
        'headers': [
            (
                b'cookie',
                f"{cookie_name}={token}".encode()
            )
        ],
    })

@pytest.mark.asyncio
async def test_access_dependency_returns_user(mock_user: User):
    db = AsyncMock(spec=AsyncSession)
    db.scalar.return_value = mock_user

    token = create_access_token(str(mock_user.id))
    request: Request = make_request('access_token', token)

    result = await get_current_user_from_access_token(request, db)

    assert result is mock_user
    db.scalar.assert_awaited_once()
