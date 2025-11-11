from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models.lecture import Lecture
from src.db.models.user import User
from src.celery_tasks.stt import transcribe_lecture  # Celery-задача STT
from src.schemas.lecture import LectureCreate, LectureRead, LectureStatus

router = APIRouter(prefix="/api/lectures", tags=["lectures"])


@router.post("/upload", response_model=LectureRead)
async def upload_lecture(
    lecture_in: LectureCreate,
    db: Session = Depends(get_db),
):
    """
    Создать новую лекцию и запустить задачу STT.
    """
    # Проверяем, существует ли пользователь
    user = db.query(User).filter(User.id == lecture_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Создаем запись лекции
    source = lecture_in.s3_url or lecture_in.file_path
    if not source:
        raise HTTPException(status_code=400, detail="Provide file_path or s3_url")

    lecture = Lecture(
        user_id=user.id,
        audio_url=source,
        text_url=None,
        status="pending"
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    # Запускаем задачу STT через Celery
    task = transcribe_lecture.delay(str(lecture.id), source)
    lecture.task_id = task.id
    db.commit()

    return lecture


@router.get("/{lecture_id}/status", response_model=LectureStatus)
def get_status(lecture_id: UUID, db: Session = Depends(get_db)):
    """
    Проверить статус лекции.
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    return {
        "lecture_id": str(lecture.id),
        "status": lecture.status,
        "task_id": lecture.task_id,
    }


@router.get("/{lecture_id}/result", response_model=LectureRead)
def get_result(lecture_id: UUID, db: Session = Depends(get_db)):
    """
    Получить результат (ссылку на текстовый файл или готовый конспект).
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    if not lecture.text_url:
        raise HTTPException(status_code=404, detail="Result not ready yet")

    return lecture
