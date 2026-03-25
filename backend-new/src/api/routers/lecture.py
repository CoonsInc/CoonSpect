from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

from src.infra.sql.session import get_db
from src.api.schemas.lecture import LectureRead, LectureUpdate, LecturesPage
import src.crud.lecture as lecture_crud
from src.infra.sql.models.user import User
from src.services.auth import authorize
from src.api.schemas.status import Status

router = APIRouter(prefix="/lecture")

@router.get("/list", response_model=LecturesPage)
async def get_list(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    user_id: UUID | None = None,
    db: AsyncSession = Depends(get_db)
):
    if limit < 1:
        raise HTTPException(400, "Too low limit value")
    
    allowed_fields = {"name", "created_at", "updated_at"}
    if sort_by not in allowed_fields:
        raise HTTPException(400, "Invalid sort field")
    
    items, total, pages = await lecture_crud.get_list(
        db, page=page, limit=limit, sort_by=sort_by, order=order, user_id=user_id
    )

    return LecturesPage(
        items = cast(list[LectureRead], items),
        total = total,
        page = page,
        pages = pages
    )

@router.get("/{lecture_id}", response_model=LectureRead)
async def get(
    lecture_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    lecture = await lecture_crud.get_by_id(db, lecture_id)
    if lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return lecture

@router.patch("/edit/{lecture_id}", response_model=LectureRead)
async def edit(
    lecture_id: UUID,
    update_data: LectureUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(authorize)
) -> Status:
    lecture = await lecture_crud.get_by_id(db, lecture_id)
    if lecture is None:
        raise HTTPException(404, "Lecture not found")
    
    if cast(UUID, user.id) != cast(UUID, lecture.user_id):
        raise HTTPException(400, "Access denied")
    
    return await lecture_crud.update(db, db_obj=lecture, update_data=update_data)

@router.delete("/delete/{lecture_id}")
async def delete(
    lecture_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(authorize)
):
    lecture = await lecture_crud.get_by_id(db, lecture_id)
    if lecture is None:
        raise HTTPException(404, "Lecture not found")
    
    if cast(UUID, user.id) != cast(UUID, lecture.user_id):
        raise HTTPException(400, "Access denied")
    
    if await lecture_crud.delete(db, lecture):
        return Status.success("Deleted successfuly")
    else:
        raise HTTPException(404, "Lecture not found")
