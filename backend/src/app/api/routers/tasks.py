from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi import UploadFile, File, Depends
from uuid import UUID, uuid4
from pathlib import Path

from src.app.api.schemas.status import Status
from src.app.api.tools import access_token_request
from src.app.api.schemas.user import UserRead
from src.app.api.tools import decode_token
from src.app.clients.s3 import get_s3_client
from src.app.settings import settings
from src.app.wsmanager import manager
from src.app.clients.celery import run_audio_pipeline, run_audio_pipeline_test
from src.app.clients.redis import redis_async
from src.app.security import TokenType

router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/start", response_model=Status)
async def start(
    file: UploadFile = File(...),
    user: UserRead = Depends(access_token_request),
    s3 = Depends(get_s3_client)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extension {ext} not allowed")
    
    if await redis_async.exists(f"task:{user.id}"):
        task_status: str = await redis_async.get(f"task:{user.id}")
        if task_status == "finish" or task_status == "error":
            await redis_async.delete(f"task:{user.id}")
        else:
            raise HTTPException(status_code=400, detail=f"Task already running")
    
    content = await file.read()

    bucket = settings.S3_RAW_LECTURES_BUCKET
    filename = f"{uuid4()}_{file.filename}"
    
    try:
        await s3.put_object(
            Bucket = bucket,
            Key = filename,
            Body = content,
            ContentType = file.content_type or "application/octet-stream",
        )
    except Exception as e:
        print(f"[TASK/START] suspitious error in start: {e}")

    if settings.BACKEND_MODE == "test":
        await run_audio_pipeline_test(user.id, bucket, filename)
    else:
        await run_audio_pipeline(user.id, bucket, filename)

    return Status.success(str(user.id))

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: UUID):
    print(f"[WS {websocket}] Connected task {task_id}")

    if not await redis_async.exists(f"task:{task_id}"):
        print(f"[WS {websocket}] task_id {task_id} not found")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Task {task_id} not found"
        )
        return

    await manager.connect(websocket, str(task_id))

    access_token_encoded = await websocket.receive_text()
    try:
        access_token = decode_token(access_token_encoded, TokenType.ACCESS)
        if access_token.uuid != task_id:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Invalid token"
            )
            return
        
    except HTTPException as e:
        print(e)
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Invalid token"
        )
        return
    
    print(f"[WS {websocket}] connection to {task_id} validated")

    await manager.send_message(str(task_id), await redis_async.get(f"task:{task_id}"))

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(str(task_id))
        print(f"[WS {websocket}] Disconnected {task_id}")
