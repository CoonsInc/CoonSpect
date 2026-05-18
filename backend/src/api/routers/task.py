from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger

from src.api.schemas.task import TaskInit, TaskStartRequest
from src.infra.db.models.user import User
from src.services.auth import authenticate
from src.services.task import TaskService, get_task_service
from src.services.websocket import WebSocketManager, get_ws_manager

router = APIRouter(prefix="/task")


@router.post("/start", response_model=TaskInit)
async def start(
    request: TaskStartRequest,
    user: User = Depends(authenticate),
    service: TaskService = Depends(get_task_service),
):
    return await service.start(user, request.filename)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(authenticate),
    ws_manager: WebSocketManager = Depends(get_ws_manager),
    service: TaskService = Depends(get_task_service),
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


@router.post("/confirm")
async def confirm_task(
    user: User = Depends(authenticate), service: TaskService = Depends(get_task_service)
):
    task_id = service.get_task_id(user)
    await service.confirm_upload_and_start(task_id, user.id)
    return {"status": "processing_started"}
