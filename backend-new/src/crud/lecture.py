import math
from uuid import UUID
from sqlalchemy import select, desc, asc, func
from sqlalchemy.orm import joinedload
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
        
        # Считаем общее количество для пагинации
        count_stmt = select(func.count(Lecture.id)).where(*filters)
        result = await self.db.execute(count_stmt)
        total = result.scalar() or 0
        
        pages = math.ceil(total / limit) if total > 0 else 1
        if page > pages or page < 1:
            return [], total, pages

        # Сортировка
        sort_func = desc if order == "desc" else asc
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

async def get_lecture_crud(db: AsyncSession = Depends(get_db)) -> LectureCRUD:
    return LectureCRUD(db)
