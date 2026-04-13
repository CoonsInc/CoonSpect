from fastapi import APIRouter, WebSocket, UploadFile, File, Depends, WebSocketDisconnect
from src.infra.sql.models.user import User
from src.services.auth import authenticate
from src.api.schemas.status import Status
from src.services.task import TaskService, get_task_service
from src.services.websocket import WebSocketManager, get_ws_manager

router = APIRouter(prefix="/task")

@router.post("/start")
async def start(
    file: UploadFile = File(...),
    user: User = Depends(authenticate),
    service: TaskService = Depends(get_task_service)
):
    async def file_chunks():
        chunk_size = 1024 * 1024  # Читаем по 1 МБ
        while chunk := await file.read(chunk_size):
            yield chunk

    task_id = await service.start(user, file.filename, file_chunks())
    
    return Status.success(task_id)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    user: User = Depends(authenticate),
    ws_manager: WebSocketManager = Depends(get_ws_manager),
    service: TaskService = Depends(get_task_service)
):
    task_id = service.get_task_id(user)
    
    task_status = await service.get_task_status(task_id)
    if not task_status:
        await websocket.close()
        return
        
    await ws_manager.connect(websocket, task_id)
    await ws_manager.send_message(task_id, task_status)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(task_id)
    except Exception:
        await ws_manager.disconnect(task_id)
        await websocket.close()
