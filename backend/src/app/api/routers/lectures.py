from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func
import math

from src.app.clients.sql.session import get_db
from src.app.clients.sql.models.lecture import Lecture
from src.app.api.schemas.lecture import LectureRead, LectureUpdate, LecturesPage

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
    
    filters = []
    if user_id:
        filters.append(Lecture.user_id == user_id)
    
    total = db.query(func.count(Lecture.id)).filter(*filters).scalar()
    pages = math.ceil(total / limit) if total > 0 else 1
    
    if page > pages or page < 1:
        return LecturesPage(items=[], total=total, page=page, pages=pages)

    offset = (page - 1) * limit

    allowed_fields = {"name", "created_at", "updated_at"}
    if sort_by not in allowed_fields:
        raise HTTPException(400, "Invalid sort field")

    sort_func = desc if order == "desc" else asc
    column = getattr(Lecture, sort_by)
    
    query = db.query(Lecture).filter(*filters).options(joinedload(Lecture.user))
    
    items = query.order_by(sort_func(column)).offset(offset).limit(limit).all()

    return LecturesPage(
        items=items,
        total=total,
        page=page,
        pages=pages
    )

@router.patch("/edit/{lecture_id}", response_model=LectureRead)
async def edit_lecture(
    lecture_id: UUID,
    update_data: LectureUpdate,
    db: Session = Depends(get_db)
):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(404, "Lecture not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(lecture, field, value)

    db.commit()
    db.refresh(lecture)
    return lecture

@router.get("/{lecture_id}", response_model=LectureRead)
async def get_lecture(lecture_id: UUID, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    return lecture
