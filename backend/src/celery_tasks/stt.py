from src.celery_app import celery_app
from src.db.session import SessionLocal
from src.db.models.lecture import Lecture
from src.wsmanager import manager
import aiohttp
import asyncio
import os
from uuid import UUID

@celery_app.task(bind=True)
def transcribe_lecture(self, lecture_id: str, audio_path: str):
    """
    Celery задача для транскрибации аудио в текст с помощью STT сервиса.
    """
    db = SessionLocal()
    try:
        # Получаем лекцию из базы
        lecture = db.query(Lecture).filter(Lecture.id == UUID(lecture_id)).first()
        if not lecture:
            raise Exception(f"Lecture {lecture_id} not found in database")
        
        print(f"[STT_TASK] Starting transcription for lecture {lecture_id}")
        
        # Отправляем обновление статуса через WebSocket
        asyncio.run(manager.send_message(lecture_id, "status:transcribing"))
        
        # Отправляем аудио в STT сервис
        result_text = asyncio.run(send_to_stt_service(audio_path))
        
        if not result_text:
            raise Exception("STT service returned empty result")
        
        print(f"[STT_TASK] Transcription completed for lecture {lecture_id}, text length: {len(result_text)}")
        
        # Сохраняем результат в файл
        text_path = f"/tmp/lectures/{lecture_id}.txt"
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        
        # Обновляем запись в базе данных
        lecture.text_url = text_path
        lecture.status = "transcribed"
        db.commit()
        
        # Отправляем обновление статуса
        asyncio.run(manager.send_message(lecture_id, "status:transcribed"))
        
        # Запускаем следующую задачу - генерацию конспекта
        # (Это можно добавить позже, для MVP пока оставим транскрибацию)
        print(f"[STT_TASK] Task completed for lecture {lecture_id}")
        
        return {
            "status": "success",
            "lecture_id": lecture_id,
            "text_path": text_path
        }
        
    except Exception as e:
        print(f"[STT_TASK] Error processing lecture {lecture_id}: {str(e)}")
        # Обновляем статус в базе при ошибке
        if lecture:
            lecture.status = "failed"
            db.commit()
            asyncio.run(manager.send_message(lecture_id, f"error:{str(e)}"))
        raise e
    finally:
        db.close()
        # Удаляем временный аудио файл
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"[STT_TASK] Temporary audio file removed: {audio_path}")

async def send_to_stt_service(audio_path: str) -> str:
    """
    Отправить аудио файл в STT сервис и получить транскрибацию.
    """
    try:
        async with aiohttp.ClientSession() as session:
            with open(audio_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename=os.path.basename(audio_path), content_type="audio/wav")
                
                async with session.post("http://stt-service:8000/transcribe", data=form) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"STT service error: {resp.status}, {error_text}")
                    
                    result = await resp.json()
                    return result.get("text", "")
    except Exception as e:
        print(f"[STT_SERVICE] Error: {str(e)}")
        raise e