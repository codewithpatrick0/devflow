import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker, 
    AsyncEngine,
)

from config import test_settings

@pytest_asyncio.fixture(scope='session')
async def test_engine():
    async_engine: AsyncEngine = create_async_engine(
        test_settings.test_database_url
    )

    try:
        yield async_engine
    finally:
        await async_engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine):
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=connection,
            join_transaction_mode='create_savepoint',
            autoflush=False,
            expire_on_commit=False
        )

        try:
            async with async_session_factory() as async_session:
                yield async_session
        finally:
            if transaction.is_active:
                await transaction.rollback()