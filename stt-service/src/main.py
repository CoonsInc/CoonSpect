from fastapi import FastAPI, UploadFile, File, HTTPException
from transcription import STTEngine
import uvicorn
import os
from typing import List

app = FastAPI(title="STT Microservice")

stt_engine = STTEngine()

ALLOWED_AUDIO_EXTENSIONS = {
    '.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.aiff'
}

ALLOWED_VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'
}

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Аудио файл"),
    language: str = "ru"
):
    
    if os.path.splitext(file.filename.lower())[1] not in ALLOWED_AUDIO_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            400, 
            "Неподдерживаемый формат файла."
        )
        
    #в идеале проврека на размер но мне лень
    
    file_type = "audio" if os.path.splitext(file.filename.lower())[1] in ALLOWED_AUDIO_EXTENSIONS else "video"
    
    audio_bytes = await file.read()
    
    try:
        segmet_text = stt_engine.transcribe(audio_bytes, language, file_type)
        full_text = " ".join(segment["text"] for segment in segmet_text["segments"])
        return {
            "status": "success",
            "text": full_text,
            "segments": segmet_text["segments"],
            "metadata": {
                "file_type": file_type,
                "language": language,
                "file_size": len(audio_bytes)
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Ошибка транскрибации: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stt"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
