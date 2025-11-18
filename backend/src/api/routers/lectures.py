from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, BackgroundTasks
from uuid import UUID
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models.lecture import Lecture
from src.db.models.user import User
from src.schemas.lecture import LectureCreate, LectureRead, LectureStatus
from src.celery_tasks.stt import transcribe_lecture
from src.wsmanager import manager
import os
import tempfile
import aiohttp
from datetime import datetime

router = APIRouter(prefix="/api/lectures", tags=["lectures"])

@router.post("/upload", response_model=LectureRead)
async def upload_lecture(
    user_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Загрузить аудио файл лекции и начать обработку.
    """
    # Проверяем, существует ли пользователь
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем формат файла
    allowed_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    # Создаем временную директорию для файлов
    os.makedirs("/tmp/lectures", exist_ok=True)
    
    try:
        # Сохраняем файл во временную директорию
        file_path = f"/tmp/lectures/{uuid.uuid4()}{file_extension}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"[UPLOAD] Saved audio file to {file_path}, size: {len(content)} bytes")
        
        # Создаем запись в базе данных
        lecture = Lecture(
            user_id=user.id,
            audio_url=file_path,  # путь к временному файлу
            text_url=None,
            status="uploading",
            task_id=None
        )
        db.add(lecture)
        db.commit()
        db.refresh(lecture)
        
        # Отправляем сообщение через WebSocket о начале загрузки
        await manager.send_message(str(lecture.id), "status:uploading")
        
        # Запускаем задачу STT через Celery
        task = transcribe_lecture.delay(str(lecture.id), file_path)
        lecture.task_id = task.id
        lecture.status = "transcribing"
        db.commit()
        
        # Отправляем обновление статуса
        await manager.send_message(str(lecture.id), "status:transcribing")
        
        return lecture
        
    except Exception as e:
        # Удаляем временный файл при ошибке
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/{lecture_id}", response_model=LectureRead)
def get_lecture(lecture_id: UUID, db: Session = Depends(get_db)):
    """
    Получить информацию о лекции по ID.
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@router.get("/{lecture_id}/status", response_model=LectureStatus)
def get_status(lecture_id: UUID, db: Session = Depends(get_db)):
    """
    Проверить статус обработки лекции.
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
    Получить результат обработки лекции (текст/конспект).
    """
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    if lecture.status != "done" and not lecture.text_url:
        raise HTTPException(status_code=400, detail="Processing not complete yet")
    
    if not lecture.text_url:
        raise HTTPException(status_code=404, detail="Result not available")
    
    return lecture

@router.get("/user/{user_id}", response_model=list[LectureRead])
def get_user_lectures(user_id: UUID, db: Session = Depends(get_db)):
    """
    Получить все лекции пользователя.
    """
    lectures = db.query(Lecture).filter(Lecture.user_id == user_id).order_by(Lecture.created_at.desc()).all()
    return lectures