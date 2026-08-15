from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.db import get_db
from devflow.app.core.security import decode_access_token, decode_refresh_token
from devflow.app.models import User
from devflow.app.repositories import UserRepository

DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenDecoder = Callable[[str], dict[str, Any]]


def get_exception_unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='invalid token',
    )


async def _get_current_user_from_token(
    request: Request,
    db: AsyncSession,
    cookie_name: str,
    decode_token: TokenDecoder,
) -> User:
    try:
        token = request.cookies.get(cookie_name)
        if not token:
            raise get_exception_unauthorized()
        payload = decode_token(token)
        user_id = int(payload['sub'])

        user = await UserRepository(db).get_by_id(user_id)
        if user is None:
            raise get_exception_unauthorized()
        return user
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise get_exception_unauthorized() from exc


async def get_current_user_from_access_token(request: Request, db: DbSession) -> User:
    return await _get_current_user_from_token(
        request=request,
        db=db,
        cookie_name='access_token',
        decode_token=decode_access_token,
    )


async def get_current_user_from_refresh_token(
    request: Request,
    db: DbSession,
) -> User:
    return await _get_current_user_from_token(
        request=request,
        db=db,
        cookie_name='refresh_token',
        decode_token=decode_refresh_token,
    )
