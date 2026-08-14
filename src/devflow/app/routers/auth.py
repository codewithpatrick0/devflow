from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.config import settings
from devflow.app.core.db import get_db
from devflow.app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError
    )
from devflow.app.schemas import (
    UserRegister,
    UserResponse,
    UserLogin
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
    status_code=status.HTTP_204_NO_CONTENT
)
async def login(data: UserLogin, response: Response, db: DbSession):
    try:
        tokens = await AuthService(db).login(data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        ) from exc 

    response.set_cookie(
        key='access_token',
        value=tokens.access_token,
        httponly=True,
        secure=False, #Para que funcione en local por ahora
        samesite='lax',
        max_age=settings.access_token_expire_minutes * 60
    )

    response.set_cookie(
        key='refresh_token',
        value=tokens.refresh_token,
        httponly=True,
        secure=False, 
        samesite='lax',
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )
        

