from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.infra.sql.models.user import User
from src.services.password import hash_password

async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create(db: AsyncSession, username: str, password_raw: str) -> User:
    user = User(username=username, password_hash=hash_password(password_raw))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
