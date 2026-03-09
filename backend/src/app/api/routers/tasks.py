from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi import UploadFile, File, Depends
from uuid import UUID
import tempfile
from src.app.api.schemas.status import Status

from src.app.api.tools import access_token_request
from src.app.api.schemas.user import UserRead
from src.app.api.tools import decode_token
from src.app.clients.s3 import get_s3_client
from src.app.config import S3_RAW_LECTURES_BUCKET
from src.app.wsmanager import manager
from src.app.clients.celery import run_audio_pipeline, run_audio_pipeline_test
from src.app.clients.redis import redis_async
from src.app.clients.sql.session import get_db
from src.app.config import BACKEND_MODE
from src.app.security import Token, TokenType

router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/start", response_model=Status)
async def start(
    file: UploadFile = File(...),
    user: UserRead = Depends(access_token_request),
    s3 = Depends(get_s3_client),
):
    await redis_async.set(f"task:{user.id}", "uploading")
    
    await s3.put_object(
        Bucket = S3_RAW_LECTURES_BUCKET,
        Key = f"{file.filename}",
        Body = await file.read(),
        ContentType = file.content_type or "application/octet-stream",
    )
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
        print(f"[UPLOAD] Saved temp file {tmp_path} ({len(content)} bytes)")

        if BACKEND_MODE == "test":
            run_audio_pipeline_test(user.id, tmp_path)
        else:
            run_audio_pipeline(user.id, tmp_path)

        return Status.success(str(user.id))
    except Exception as e:
        print(f"[UPLOAD] Error processing task {user.id}: {e}")
        await manager.send_message(user.id, f"error: {str(e)}")
        manager.disconnect(user.id)
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    print(f"[WS] Connected task {user_id}")

    if not await redis_async.exists(f"task:{user_id}"):
        print(f"[WS] task_id {user_id} not found")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Task {user_id} not found"
        )
        return

    await manager.connect(websocket, str(user_id))

    access_token_encoded = await websocket.receive_text()
    try:
        access_token = decode_token(access_token_encoded, TokenType.ACCESS)
        if access_token.uuid != user_id:
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

    await manager.send_message(user_id, await redis_async.get(f"task:{user_id}"))

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(str(user_id))
        print(f"[WS] Disconnected {user_id}")
