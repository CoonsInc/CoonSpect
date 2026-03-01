from fastapi import APIRouter, HTTPException
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi import UploadFile, File
from uuid import UUID, uuid4
import tempfile
from src.app.api.schemas.status import Status

from src.app.wsmanager import manager
from src.app.celery_app import run_audio_pipeline, run_audio_pipeline_test
from src.app.db.redis import redis_sync as r

router = APIRouter(prefix="/task", tags=["tasks"])

@router.get("/create", response_model=Status)
async def create_task():
    """
    Создать задачу
    """
    task_id = uuid4()
    r.set(f"task:{task_id}", "uploading")
    print(f"[TASK/CREATE] Created new task_id={task_id}")
    return Status.success(task_id)

@router.get("/correct/{task_id}", response_model=Status)
async def check_task_id(task_id: UUID):
    """
    Проверить что задача существует
    """
    if r.exists(f"task_status:{task_id}"):
        print(f"[TASK/correct] Correct task_id={task_id}")
        return Status.success()
    
    print(f"[TASK/correct] Incorrect task_id={task_id}")
    raise HTTPException(status_code=400, detail="Incorrect task_id")

@router.post("/start/{task_id}", response_model=Status)
async def start(task_id: UUID, file: UploadFile = File(...)):
    """
    Запустить задачу
    """
    print(f"[TASK/START] Task {task_id}, got file {file.filename}")
    
    if not r.exists(f"task:{task_id}"):
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
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
    await manager.send_message(task_id, r.get(f"task:{task_id}"))
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)
        print(f"[WS] Disconnected {task_id}")
