from src.celery_app import app
import requests
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.db.models.lecture import Lecture
from src.db.models.transcription import Transcription
from src.config import STT_SERVICE_URL
from sqlalchemy.exc import SQLAlchemyError

@app.task(bind=True, name="tasks.transcribe_lecture")
def transcribe_lecture(self, lecture_id: str, source: str):
    session: Session = SessionLocal()
    try:
        lecture = session.query(Lecture).filter(Lecture.id == lecture_id).one_or_none()
        if not lecture:
            return {"error": "lecture not found"}

        lecture.status = "transcribing"
        lecture.task_id = self.request.id
        session.commit()

        # Вызов STT-сервиса — отправляем JSON с ссылкой или локальным путём
        resp = requests.post(STT_SERVICE_URL, json={"path": source}, timeout=300)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "success":
            lecture.status = "failed"
            session.commit()
            return {"error": "stt failed", "detail": data}

        text = data["text"]

        # Сохраняем транскрипт
        tr = Transcription(lecture_id=lecture.id, text=text)
        session.add(tr)
        lecture.status = "transcribed"
        session.commit()
        return {"status": "ok", "lecture_id": str(lecture.id)}
    except Exception as e:
        session.rollback()
        if lecture:
            lecture.status = "failed"
            session.commit()
        raise
    finally:
        session.close()
