import math
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, collate, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.common.sorting import LectureSortBy, SortOrder
from src.crud.base import BaseCRUD
from src.infra.db.models.lecture import Lecture
from src.infra.db.session import get_db


class LectureCRUD(BaseCRUD[Lecture]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lecture, db)

    async def get_list(
        self,
        page: int,
        limit: int,
        sort_by: LectureSortBy,
        order: SortOrder,
        user_id: UUID | None = None,
        search_name: str | None = None,
        requester_user_id: UUID | None = None,
    ) -> tuple[list[Lecture], int, int]:
        if user_id is not None:
            if requester_user_id == user_id:
                filters = [Lecture.user_id == user_id]
            else:
                filters = [Lecture.user_id == user_id, Lecture.public.is_(True)]
        else:
            filters = [Lecture.public.is_(True)]

        if search_name:
            filters.append(Lecture.name.ilike(f"%{search_name}%"))

        count_stmt = select(func.count(Lecture.id)).where(*filters)
        result = await self.db.execute(count_stmt)
        total = result.scalar() or 0

        pages = math.ceil(total / limit) if total > 0 else 1
        if page > pages or page < 1:
            return [], total, pages

        sort_func = desc if order == SortOrder.DESC else asc
        if sort_by == LectureSortBy.NAME:
            if self.db.bind.dialect.name == "postgresql":
                column = collate(Lecture.name, "C")
            else:
                column = Lecture.name
        else:
            column = getattr(Lecture, sort_by.value, Lecture.created_at)

        stmt = (
            select(Lecture)
            .where(*filters)
            .options(joinedload(Lecture.user))
            .order_by(sort_func(column))
            .offset((page - 1) * limit)
            .limit(limit)
        )

        res = await self.db.execute(stmt)
        return list(res.unique().scalars().all()), total, pages

    async def read_with_user(self, id: UUID) -> Lecture | None:
        """Получает лекцию вместе с пользователем (один дополнительный запрос)."""
        stmt = (
            select(Lecture).where(Lecture.id == id).options(selectinload(Lecture.user))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


async def get_lecture_crud(db: AsyncSession = Depends(get_db)) -> LectureCRUD:
    return LectureCRUD(db)
