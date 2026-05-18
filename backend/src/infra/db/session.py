from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.settings import settings


@lru_cache
def get_engine():
    return create_async_engine(settings.POSTGRES_URL, pool_pre_ping=True)


@lru_cache
def get_session_factory():
    return async_sessionmaker(
        bind=get_engine(), class_=AsyncSession, expire_on_commit=False
    )


async def get_db():
    Session = get_session_factory()
    async with Session() as session:
        yield session
