from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import os
import time
from datetime import datetime

from schemas import RequestTranscribeSTT
from s3 import get_s3_client, download_from_s3
from settings import settings

app = FastAPI(title="Mock STT Microservice", description="Простая заглушка")

MOCK_TEXT = "Это тестовый текст для транскрипции. Заглушка всегда возвращает одно и то же."

MOCK_SEGMENTS = [
    {"start": 0.0, "end": 2.0, "text": "Это тестовый текст для транскрипции."},
    {"start": 2.0, "end": 5.0, "text": "Заглушка всегда возвращает одно и то же."}
]

@app.post("/transcribe")
async def transcribe_audio(
    content: RequestTranscribeSTT,
    language: str = "ru",
    s3_client = Depends(get_s3_client)
):
    file_ext = os.path.splitext(content.filename.lower())[1]

    print(content.filename, file_ext)
    
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")
    
    tmp_file_path = await download_from_s3(s3_client, content.bucket, content.filename)
    file_size = tmp_file_path.stat().st_size
    tmp_file_path.unlink(missing_ok = True)
    
    time.sleep(5)
    
    return {
        "status": "success",
        "text": MOCK_TEXT,
        "segments": MOCK_SEGMENTS,
        "metadata": {
            "original_filename": content.filename,
            "file_size": file_size,
            "processing_time": 5.0,
            "is_mock": True,
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mock-stt",
        "message": "Простая заглушка работает"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)