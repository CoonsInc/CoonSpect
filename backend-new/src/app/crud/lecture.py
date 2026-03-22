from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func
import math

from src.app.infra.sql.models.lecture import Lecture
from src.app.api.schemas.lecture import LectureUpdate, LectureCreate, LectureDelete

def get_list(
    db: Session, 
    page: int = 1, 
    limit: int = 20, 
    sort_by: str = "created_at", 
    order: str = "desc", 
    user_id: UUID | None = None
):
    filters = []
    if user_id:
        filters.append(Lecture.user_id == user_id)
    
    total = db.query(func.count(Lecture.id)).filter(*filters).scalar()
    pages = math.ceil(total / limit) if total > 0 else 1
    
    if page > pages or page < 1:
        return [], total, pages

    offset = (page - 1) * limit
    sort_func = desc if order == "desc" else asc
    column = getattr(Lecture, sort_by)

    items = (
        db.query(Lecture)
        .filter(*filters)
        .options(joinedload(Lecture.user))
        .order_by(sort_func(column))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return items, total, pages

def get_by_id(db: Session, lecture_id: UUID) -> Lecture | None:
    return db.query(Lecture).filter(Lecture.id == lecture_id).first()

def update(db: Session, db_obj: Lecture, update_data: LectureUpdate) -> Lecture:
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(db_obj, field, value)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create(db: Session, obj_in: LectureCreate, user_id: UUID) -> Lecture:
    db_obj = Lecture(**obj_in.model_dump(), user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, lecture_id: LectureDelete) -> bool:
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        return False
    db.delete(lecture)
    db.commit()
    return True