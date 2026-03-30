from fastapi import APIRouter, WebSocket, UploadFile, File, Depends
from uuid import uuid4
from src.settings import settings
from src.infra.sql.models.user import User
from src.services.auth import authorize
from src.infra.tasks.tasks import run_audio_pipeline
from src.api.schemas.status import Status
# Предположим, у вас есть сервис для работы с S3
# from src.services.s3 import s3_service 

router = APIRouter(prefix="/task")

@router.post("/start")
async def start(
    file: UploadFile = File(...),
    user: User = Depends(authorize)
):
    # 1. Загружаем файл в S3 (STT сервису нужен доступ к файлу)
    # filename = await s3_service.upload(file)
    bucket = settings.S3_RAW_LECTURES_BUCKET
    filename = f"{uuid4()}_{file.filename}"
    
    task = await run_audio_pipeline.kiq(
        user.id,
        bucket, 
        filename
    )
    
    return Status.success(task.task_id)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Status for {client_id}: Processing...")
    except Exception:
        await websocket.close()
