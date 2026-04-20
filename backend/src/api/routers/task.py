from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from src.infra.sql.models.user import User
from src.services.auth import authenticate
from src.api.schemas.task import TaskInit
from src.services.task import TaskService, get_task_service
from src.services.websocket import WebSocketManager, get_ws_manager
from loguru import logger

router = APIRouter(prefix="/task")

@router.post("/start", response_model=TaskInit)
async def start(
    user: User = Depends(authenticate),
    service: TaskService = Depends(get_task_service)
):
    return await service.start(user)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    user: User = Depends(authenticate),
    ws_manager: WebSocketManager = Depends(get_ws_manager),
    service: TaskService = Depends(get_task_service)
):
    task_id = service.get_task_id(user)
    first_msg = await service.ws_start(task_id)

    if not first_msg:
        logger.warning(f"User {user.id} don't have task to be tracked")
        await websocket.close()
        return
        
    await ws_manager.connect(websocket, task_id)
    await ws_manager.send_message(task_id, first_msg)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(task_id)
    except Exception:
        await ws_manager.disconnect(task_id)
        await websocket.close()
