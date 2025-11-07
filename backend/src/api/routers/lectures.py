from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models.lecture import Lecture
from src.db.models.user import User
from src.celery_tasks.stt import transcribe_lecture

router = APIRouter(prefix="/api", tags=["lectures"])


@router.post("/upload")
async def upload(
    file_path: str | None = None,
    s3_url: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Создать новую лекцию и запустить задачу STT.
    """
    if not file_path and not s3_url:
        raise HTTPException(400, "Provide file_path or s3_url")

    source = file_path or s3_url

    # временно выбираем первого пользователя (MVP)
    user = db.query(User).first()
    if not user:
        raise HTTPException(400, "No users exist. Create a user first.")

    lecture = Lecture(user_id=user.id, audio_url=source, status="pending")
    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    task = transcribe_lecture.delay(str(lecture.id), source)
    lecture.task_id = task.id
    db.commit()

    return {
        "lecture_id": str(lecture.id),
        "user_id": str(user.id),
        "status": lecture.status,
    }


@router.get("/status/{lecture_id}")
def status(lecture_id: UUID, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).one_or_none()
    if not lecture:
        raise HTTPException(404, "not found")
    return {
        "lecture_id": str(lecture.id),
        "status": lecture.status,
        "task_id": lecture.task_id,
    }


@router.get("/result/{lecture_id}")
def result(lecture_id: UUID, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).one_or_none()
    if not lecture:
        raise HTTPException(404, "not found")

    if lecture.transcription is None:
        raise HTTPException(404, "transcription not ready")

    return {
        "lecture_id": str(lecture.id),
        "transcription": lecture.transcription.text,
    }
