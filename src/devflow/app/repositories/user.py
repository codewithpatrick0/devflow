from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from devflow.app.models import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        return await self.db.scalar(select(User).where(User.username == username))

    async def get_by_email(self, email: str) -> User | None:
        return await self.db.scalar(select(User).where(User.email == email))

    def add(self, user: User) -> None:
        # No commit here on purpose: the transaction belongs to the service,
        # which may need several repositories to succeed or fail together.
        self.db.add(user)
