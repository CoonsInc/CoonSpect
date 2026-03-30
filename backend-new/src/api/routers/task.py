from fastapi import APIRouter, WebSocket, UploadFile, File, Depends
from src.infra.sql.models.user import User
from src.services.auth import authorize
from src.api.schemas.status import Status
from src.services.task import TaskService, get_task_service

router = APIRouter(prefix="/task")

@router.post("/start")
async def start(
    file: UploadFile = File(...),
    user: User = Depends(authorize),
    service: TaskService = Depends(get_task_service)
):
    async def file_chunks():
        chunk_size = 1024 * 1024  # Читаем по 1 МБ
        while chunk := await file.read(chunk_size):
            yield chunk

    task_id = await service.run_audio_pipeline(
        user_id = user.id,
        original_filename = file.filename,
        file_content = file_chunks()
    )
    
    return Status.success(task_id)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    client_id: str,
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Status for {client_id}: Processing...")
            
    except Exception:
        # Корректно закрываем соединение при обрыве
        await websocket.close()