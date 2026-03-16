from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi import UploadFile, File, Depends
from uuid import UUID, uuid4
from pathlib import Path
from http.cookies import SimpleCookie

from src.app.api.schemas.status import Status
from src.app.api.tools import decode_token
from src.app.clients.s3 import get_s3_client
from src.app.settings import settings
from src.app.wsmanager import manager
from src.app.clients.celery import run_audio_pipeline, run_audio_pipeline_test
from src.app.clients.redis import redis_async
from src.app.security import TokenType
from src.app.api.tools import get_current_user
from src.app.clients.sql.models import User

router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/start", response_model=Status)
async def start(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
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

    return Status.success()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"[WS] WS STARTING")
    
    print(f"[WS] {websocket.headers.items()}")

    task_id = None

    cookie_header = websocket.headers.get("cookie")
    if not cookie_header:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No cookies")
        return
    
    cookies = SimpleCookie(cookie_header)
    access_token_value = cookies.get("access_token")
    
    if not access_token_value:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No access token")
        return
    
    try:
        token_data = decode_token(access_token_value.value, TokenType.ACCESS)
        
        # Проверка блэклиста (async)
        if await redis_async.get(f"blacklist:{access_token_value.value}"):
            raise HTTPException(401, "Token revoked")
        
        task_id = token_data.uuid
            
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return
    
    if not await redis_async.exists(f"task:{task_id}"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Task not found")
        return
    
    await manager.connect(websocket, str(task_id))
    print(f"[WS {websocket}] Connected & Authed task {task_id}")

    await manager.send_message(str(task_id), await redis_async.get(f"task:{task_id}"))

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(str(task_id))
        print(f"[WS {websocket}] Disconnected {task_id}")
