from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc, asc, func
from loguru import logger
import math

from src.infra.sql.models.lecture import Lecture
from src.api.schemas.lecture import LectureUpdate, LectureCreate

async def get_list(
    db: AsyncSession, 
    page: int = 1, 
    limit: int = 20, 
    sort_by: str = "created_at", 
    order: str = "desc", 
    user_id: UUID | None = None
) -> tuple[list[Lecture], int, int]:
    filters = []
    if user_id is not None:
        filters.append(Lecture.user_id == user_id)
    
    count_stmt = select(func.count(Lecture.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
        
    result = await db.execute(count_stmt)
    total: int | None = result.scalar()
    
    if total is None:
        logger.error("Unexpected total == None")
        raise Exception("Unexpected total == None")

    pages = math.ceil(total / limit) if total > 0 else 1
    
    if page > pages or page < 1:
        return [], total, pages

    offset = (page - 1) * limit
    sort_func = desc if order == "desc" else asc
    column = getattr(Lecture, sort_by)

    stmt = (
        select(Lecture)
        .where(*filters)
        .options(joinedload(Lecture.user))
        .order_by(sort_func(column))
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    return items, total, pages

async def get_by_id(db: AsyncSession, lecture_id: UUID) -> Lecture | None:
    stmt = select(Lecture).where(Lecture.id == lecture_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create(db: AsyncSession, obj_in: LectureCreate) -> Lecture:
    db_obj = Lecture(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update(db: AsyncSession, db_obj: Lecture, update_data: LectureUpdate) -> Lecture:
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete(db: AsyncSession, db_obj: Lecture) -> bool:
    await db.delete(db_obj)
    await db.commit()
    return True
