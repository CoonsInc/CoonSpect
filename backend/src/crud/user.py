from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import BaseCRUD
from src.infra.db.models.user import User
from src.infra.db.session import get_db


class UserCRUD(BaseCRUD[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def read_by_username(self, username: str) -> User | None:
        """Уникальный поиск для логина."""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()


async def get_user_crud(db: AsyncSession = Depends(get_db)) -> UserCRUD:
    return UserCRUD(db)
