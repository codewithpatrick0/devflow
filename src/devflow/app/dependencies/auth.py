from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.db import get_db
from devflow.app.core.security import decode_access_token
from devflow.app.models import User
from devflow.app.repositories import UserRepository

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_exception_unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='invalid token',
    )


async def get_current_user(request: Request, db: DbSession) -> User:
    try:
        token = request.cookies.get('access_token')
        if not token:
            raise get_exception_unauthorized()
        payload = decode_access_token(token)
        user = await UserRepository(db).get_by_id(int(payload.get('sub')))
        if user is None:
            raise get_exception_unauthorized()
        return user
    except jwt.InvalidTokenError as exc:
        raise get_exception_unauthorized() from exc
