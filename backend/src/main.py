from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.users import router as user_router
from src.api.routers.lectures import router as lecture_router
from src.celery_app import celery_app
from src.db.session import get_db
from src.db.models.lecture import Lecture
from src.db.models.user import User
from src.wsmanager import manager
from sqlalchemy.orm import Session
import uuid
import os
import tempfile
import aiohttp
from contextlib import asynccontextmanager

# Lifespan manager для инициализации приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("[SERVER] Starting up CoonSpect backend...")
    yield
    # Shutdown code
    print("[SERVER] Shutting down CoonSpect backend...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включаем роутеры
app.include_router(user_router)
app.include_router(lecture_router)

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "CoonSpect Backend"}

@app.websocket("/ws/{lecture_id}")
async def websocket_endpoint(websocket: WebSocket, lecture_id: str):
    try:
        # Проверяем, существует ли лекция
        db = next(get_db())
        lecture = db.query(Lecture).filter(Lecture.id == uuid.UUID(lecture_id)).first()
        if not lecture:
            await websocket.close(code=4004, reason="Lecture not found")
            return
        
        await manager.connect(websocket, lecture_id)
        await manager.send_message(lecture_id, f"status:{lecture.status}")
        
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(lecture_id)
            print(f"[WS] Client disconnected from lecture {lecture_id}")
    except Exception as e:
        print(f"[WS] Error: {e}")
        await websocket.close(code=4000, reason=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)