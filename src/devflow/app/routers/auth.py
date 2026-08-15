from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.config import settings
from devflow.app.core.db import get_db
from devflow.app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from devflow.app.dependencies.auth import (
    get_current_user_from_access_token,
    get_current_user_from_refresh_token,
)
from devflow.app.models import User
from devflow.app.schemas import (
    UserLogin,
    UserRegister,
    UserResponse,
)
from devflow.app.services import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: UserRegister, db: DbSession):
    try:
        return await AuthService(db).register(data)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    '/login',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def login(data: UserLogin, response: Response, db: DbSession):
    try:
        tokens = await AuthService(db).login(data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    response.set_cookie(
        key='access_token',
        value=tokens.access_token,
        httponly=True,
        secure=False,  # Works over local HTTP during development.
        samesite='lax',
        max_age=settings.access_token_expire_minutes * 60,
    )

    response.set_cookie(
        key='refresh_token',
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.get('/me', response_model=UserResponse)
async def me(user: User = Depends(get_current_user_from_access_token)):
    return user


@router.post(
    '/refresh',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def refresh(
    db: DbSession,
    response: Response,
    user: User = Depends(get_current_user_from_refresh_token),
):
    token = AuthService(db).refresh(user)

    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=settings.access_token_expire_minutes * 60,
    )


@router.post(
    '/logout',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
