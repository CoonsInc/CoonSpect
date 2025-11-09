from src.api.routers.users import router as user_router
from src.api.routers.lectures import router as lecture_router
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from celery import chain
from celery_app import *
import aiohttp
import tempfile
import os
import json
from wsmanager import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks: dict[int, str] = {}
tasks_result: dict[int, str] = {}

@app.get("/")
async def health_check():
    print("[SERVER] Health check OK")
    return {"status": "ok"}

app.include_router(user_router)
app.include_router(lecture_router)

@app.get("/create_task")
def create_task():
    task_id = 0 if not tasks else max(tasks.keys()) + 1
    tasks[task_id] = "uploading"
    print(f"[CREATE_TASK] Created new task_id={task_id}, current tasks={list(tasks.keys())}")
    return {"task_id": task_id}

@app.get("/correct_task_id/{task_id}")
async def check_task_id(task_id: int, sender: str = None):
    print(f"[CORRECT_TASK] Checking {task_id} from sender={sender}")
    if task_id in tasks:
        tasks[task_id] = sender or tasks[task_id]
        await manager.send_message(task_id, sender or "unknown")
        return {"status": "correct"}
    print(f"[CORRECT_TASK] Invalid task_id={task_id}")
    return {"status": "incorrect"}

@app.post("/finish")
async def finish(content: dict):
    print(f"[FINISH] Received: {content}")
    if content.get("task_id") not in tasks:
        print("[FINISH] Task not found!")
        return {"status": "unsuccess"}
    
    tid = content["task_id"]
    tasks.pop(tid, None)
    tasks_result[tid] = content["content"]
    print(f"[FINISH] Task {tid} finished. Result length={len(content['content'])}")
    await manager.send_message(tid, "finish")
    return {"status": "success"}

@app.post("/upload_audio/{task_id}")
async def upload_audio(task_id: int, file: UploadFile = File(...)):
    print(f"[UPLOAD] Task {task_id}, got file {file.filename}")
    
    if task_id not in tasks:
        return {"status": "error", "reason": "invalid task_id"}

    tmp_path = None
    try:
        # сохраняем временно файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
        print(f"[UPLOAD] Saved temp file {tmp_path} ({len(content)} bytes)")

        # отправляем сообщение клиенту (через WS)
        await manager.send_message(task_id, "stt")

        # отправляем файл в STT сервис
        async with aiohttp.ClientSession() as session:
            with open(tmp_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename=file.filename, content_type="audio/wav")

                async with session.post("http://stt-service:8000/transcribe", data=form) as resp:
                    if resp.status != 200:
                        error_msg = f"STT service error: {resp.status}"
                        await manager.send_message(task_id, f"error: {error_msg}")
                        return {"status": "stt_error", "message": error_msg}

                    result = await resp.json()
                    text = result.get("text", "")
                    tasks_result[task_id] = text
                    await manager.send_message(task_id, "finish")

        return {"status": "success"}

    except Exception as e:
        print(f"[UPLOAD] Error processing task {task_id}: {e}")
        await manager.send_message(task_id, f"error: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            print(f"[UPLOAD] Temp file {tmp_path} deleted")


@app.post("/result/{task_id}")
async def get_result(task_id: int):
    print(f"[RESULT] Request for task_id={task_id}")
    if task_id not in tasks_result:
        print(f"[RESULT] Task {task_id} not found in results")
        return {"exist": False, "content": None}
    print(f"[RESULT] Returning content for task_id={task_id}, len={len(tasks_result[task_id])}")
    return {"exist": True, "content": tasks_result[task_id]}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    print(f"[WS] Connected task {task_id}")
    await manager.connect(websocket, task_id)   # сохраняем соединение по task_id
    await manager.send_message(task_id, "ready") # сразу сообщаем фронту, что WS готов

    try:
        while True:
            await websocket.receive_text()       # просто ждём, пока клиент не отвалится
    except WebSocketDisconnect:
        manager.disconnect(task_id)
        print(f"[WS] Disconnected {task_id}")