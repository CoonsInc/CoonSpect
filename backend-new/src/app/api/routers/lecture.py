from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from typing import cast

from src.app.infra.sql.session import get_db
from src.app.api.schemas.lecture import LectureRead, LectureUpdate, LecturesPage
import src.app.crud.lecture as lecture_crud

router = APIRouter(prefix="/lecture")

@router.get("/list", response_model=LecturesPage)
async def get_lectures(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    user_id: UUID | None = None,
    db: Session = Depends(get_db)
):
    if limit < 1:
        raise HTTPException(400, "Too low limit value")
    
    allowed_fields = {"name", "created_at", "updated_at"}
    if sort_by not in allowed_fields:
        raise HTTPException(400, "Invalid sort field")

    items, total, pages = lecture_crud.get_list(
        db, page=page, limit=limit, sort_by=sort_by, order=order, user_id=user_id
    )

    return LecturesPage(
        items = cast(list[LectureRead], items),
        total = total,
        page = page,
        pages = pages
    )

@router.patch("/edit/{lecture_id}", response_model=LectureRead)
async def edit_lecture(
    lecture_id: UUID,
    update_data: LectureUpdate,
    db: Session = Depends(get_db)
):
    lecture = lecture_crud.get_by_id(db, lecture_id)
    if not lecture:
        raise HTTPException(404, "Lecture not found")
    
    return lecture_crud.update(db, db_obj=lecture, update_data=update_data)

@router.get("/{lecture_id}", response_model=LectureRead)
async def get_lecture(lecture_id: UUID, db: Session = Depends(get_db)):
    lecture = lecture_crud.get_by_id(db, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture