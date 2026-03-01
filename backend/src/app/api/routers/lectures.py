from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.db.models.lecture import Lecture
from src.app.api.schemas.lecture import LectureRead

router = APIRouter(prefix="/lectures", tags=["lectures"])

@router.get("/{lecture_id}", response_model=LectureRead)
async def get_result(lecture_id: UUID, db: Session = Depends(get_db)):
    """
    Получить результат (ссылку на текстовый файл или готовый конспект).
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    if not lecture.text:
        raise HTTPException(status_code=400, detail="Result not ready yet")

    return lecture
