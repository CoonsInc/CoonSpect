from fastapi import FastAPI, HTTPException, Depends
from transcription import STTEngine
import uvicorn
import os

from settings import settings
from schemas import RequestTranscribeSTT
from s3 import download_from_s3, get_s3_client

app = FastAPI(title="STT Microservice")

stt_engine = STTEngine()

@app.post("/transcribe")
async def transcribe_audio(
    content: RequestTranscribeSTT,
    language: str = "ru",
    s3_client = Depends(get_s3_client)
):
    if os.path.splitext(content.filename.lower())[1] not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Неподдерживаемый формат файла.")
        
    #в идеале проврека на размер но мне лень
    
    file_type = "audio" if os.path.splitext(content.filename.lower())[1] in settings.ALLOWED_AUDIO_EXTENSIONS else "video"
    
    tmp_file_path = await download_from_s3(s3_client, content.bucket, content.filename)
    
    try:
        file_size = tmp_file_path.stat().st_size
        segmet_text = stt_engine.transcribe(tmp_file_path, language, file_type)
        full_text = " ".join(segment["text"] for segment in segmet_text["segments"])
        return {
            "status": "success",
            "text": full_text,
            "segments": segmet_text["segments"],
            "metadata": {
                "file_type": file_type,
                "language": language,
                "file_size": file_size
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Ошибка транскрибации: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stt"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
