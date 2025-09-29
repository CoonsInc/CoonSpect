from fastapi import FastAPI, UploadFile, File, HTTPException
from transcription import STTEngine
import uvicorn

app = FastAPI(title="STT Microservice")

stt_engine = STTEngine()

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Аудио файл"),
    language: str = "ru"
):
    audio_bytes = await file.read()
    
    #validate_file(file, audio_bytes)
    
    try:
        text = stt_engine.transcribe(audio_bytes, language)
        return {
            "status": "success",
            "text": text,
            "language": language,
            "file_size": len(audio_bytes)
        }
    except Exception as e:
        raise HTTPException(500, f"Ошибка транскрибации: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stt"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)