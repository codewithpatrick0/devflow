from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.db import get_db
from devflow.app.core.exceptions import UserAlreadyExistsError
from devflow.app.schemas.user import UserRegister, UserResponse
from devflow.app.services import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: UserRegister, db: DbSession):
    # The service speaks the domain language; translating that into HTTP is
    # the router's job, so the service stays usable outside of a request.
    try:
        return await AuthService(db).register(data)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
