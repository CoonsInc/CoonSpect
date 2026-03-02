from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi import UploadFile, File, Depends
from uuid import UUID, uuid4
import tempfile
from src.app.api.schemas.status import Status

from src.app.wsmanager import manager
from src.app.celery_app import run_audio_pipeline, run_audio_pipeline_test
from src.app.db.redis import redis_sync as r
from src.app.api.tools import access_token_request
from src.app.api.schemas.user import UserRead
from src.app.api.tools import decode_token
from src.app.db.s3 import get_s3_client
from src.app.config import S3_RAW_LECTURES_BUCKET

router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/start/{task_id}", response_model=Status)
async def start(
    file: UploadFile = File(...),
    user: UserRead = Depends(access_token_request),
    s3 = Depends(get_s3_client),
):
    task_id = uuid4()

    r.set(f"user:{user.id}:task:{task_id}", "uploading")
    
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

        run_audio_pipeline_test(task_id, tmp_path)

        return Status.success()
    except Exception as e:
        print(f"[UPLOAD] Error processing task {task_id}: {e}")
        await manager.send_message(task_id, f"error: {str(e)}")
        manager.disconnect(task_id)
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: UUID):
    """
    Отслеживание состояния задачи
    """
    print(f"[WS] Connected task {task_id}")

    if not r.exists(f"task:{task_id}"):
        print(f"[WS] task_id {task_id} not found")
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Task {task_id} not found"
        )
        return

    await manager.connect(websocket, task_id)

    access_token = await websocket.receive_text()
    decode_token(access_token, "access")

    await manager.send_message(task_id, r.get(f"task:{task_id}"))
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)
        print(f"[WS] Disconnected {task_id}")
