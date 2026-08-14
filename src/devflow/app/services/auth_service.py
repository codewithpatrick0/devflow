from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from devflow.app.core.exceptions import UserAlreadyExistsError
from devflow.app.core.security import hash_password
from devflow.app.models import User
from devflow.app.repositories import UserRepository
from devflow.app.schemas.user import UserRegister


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
