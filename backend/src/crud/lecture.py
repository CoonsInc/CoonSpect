import math
from uuid import UUID
from sqlalchemy import select, desc, asc, func, collate
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.crud.base import BaseCRUD
from src.infra.sql.models.lecture import Lecture
from src.infra.sql.session import get_db

class LectureCRUD(BaseCRUD[Lecture]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lecture, db)

    async def get_list(
        self, 
        page: int = 1, 
        limit: int = 20, 
        sort_by: str = "created_at", 
        order: str = "desc", 
        user_id: UUID | None = None
    ) -> tuple[list[Lecture], int, int]:
        filters = []
        if user_id:
            filters.append(Lecture.user_id == user_id)
        
        # подсчёт общего количества
        count_stmt = select(func.count(Lecture.id)).where(*filters)
        result = await self.db.execute(count_stmt)
        total = result.scalar() or 0
        
        pages = math.ceil(total / limit) if total > 0 else 1
        if page > pages or page < 1:
            return [], total, pages
        
        sort_func = desc if order == "desc" else asc
        if sort_by == "name":
            if self.db.bind.dialect.name == "postgresql":
                column = collate(Lecture.name, "C")
            else:
                column = Lecture.name
        else:
            column = getattr(Lecture, sort_by, Lecture.created_at)

        stmt = (
            select(Lecture)
            .where(*filters)
            .options(joinedload(Lecture.user))
            .order_by(sort_func(column))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total, pages
    
    async def read_with_user(self, id: UUID) -> Lecture | None:
        """Получает лекцию вместе с пользователем (один дополнительный запрос)."""
        stmt = select(Lecture).where(Lecture.id == id).options(selectinload(Lecture.user))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

async def get_lecture_crud(db: AsyncSession = Depends(get_db)) -> LectureCRUD:
    return LectureCRUD(db)
