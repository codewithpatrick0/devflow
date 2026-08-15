from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from devflow.app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from devflow.app.models import User
from devflow.app.repositories import UserRepository
from devflow.app.schemas.token import TokensResponse
from devflow.app.schemas.user import UserLogin, UserRegister

# Verified when the email does not exist, so a missing account costs the same
# as a wrong password. Without it the response time alone tells an attacker
# which emails are registered.
_DUMMY_HASH = hash_password('not-a-real-password')


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def register(self, data: UserRegister) -> User:
        if await self.users.get_by_email(data.email):
            raise UserAlreadyExistsError('email')

        if await self.users.get_by_username(data.username):
            raise UserAlreadyExistsError('username')

        user = User(
            email=data.email,
            username=data.username,
            password_hash=hash_password(data.password),
        )
        self.users.add(user)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise UserAlreadyExistsError('email or username') from exc

        await self.db.refresh(user)

        return user

    async def login(self, data: UserLogin) -> TokensResponse:
        user = await self.users.get_by_email(data.email)

        if user is None:
            verify_password(data.password, _DUMMY_HASH)
            raise InvalidCredentialsError()

        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()

        subject = str(user.id)

        return TokensResponse(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

    def refresh(self, user: User) -> str:
        return create_access_token(str(user.id))
