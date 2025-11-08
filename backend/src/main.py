from src.api.routers.users import router as user_router
from src.api.routers.lectures import router as lecture_router
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from celery import chain
from celery_app import *
import base64
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
    print(f"[WS] Connection attempt for task_id={task_id}")
    if task_id not in tasks:
        print(f"[WS] Invalid task_id={task_id}, closing connection.")
        await websocket.close(code=4000)
        return

    await manager.connect(websocket, task_id)
    await manager.send_message(task_id, tasks[task_id])
    print(f"[WS] WebSocket connected for task {task_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"[WS:{task_id}] Received raw data: {data[:100]}...")

            try:
                payload = json.loads(data)
            except Exception as e:
                print(f"[WS:{task_id}] Invalid JSON: {e}")
                continue

            if payload.get("type") == "file":
                filename = payload.get("filename", f"task_{task_id}.wav")
                print(f"[WS:{task_id}] File received: {filename}")

                content_b64 = payload.get("content")
                if not content_b64:
                    print(f"[WS:{task_id}] Missing content field")
                    await manager.send_message(task_id, "error: no content")
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                    audio_bytes = base64.b64decode(content_b64)
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                print(f"[WS:{task_id}] Temporary file saved at {tmp_path} ({len(audio_bytes)} bytes)")

                await manager.send_message(task_id, "stt")

                try:
                    async with aiohttp.ClientSession() as session:
                        with open(tmp_path, "rb") as f:
                            form = aiohttp.FormData()
                            form.add_field("file", f, filename=filename, content_type="audio/wav")

                            print(f"[WS:{task_id}] Sending file to STT service...")
                            async with session.post("http://stt-service:8000/transcribe", data=form) as resp:
                                print(f"[WS:{task_id}] STT response status={resp.status}")
                                if resp.status != 200:
                                    await manager.send_message(task_id, f"error: stt failed {resp.status}")
                                    continue

                                stt_result = await resp.json()
                                text = stt_result.get("text", "")
                                print(f"[WS:{task_id}] STT text received ({len(text)} chars)")
                                tasks_result[task_id] = text
                                await manager.send_message(task_id, "finish")

                except Exception as e:
                    print(f"[WS:{task_id}] STT error: {e}")
                    await manager.send_message(task_id, f"error: {e}")

                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        print(f"[WS:{task_id}] Temp file {tmp_path} deleted")

            else:
                print(f"[WS:{task_id}] Unknown message type: {payload.get('type')}")

    except WebSocketDisconnect:
        print(f"[WS:{task_id}] Client disconnected")
    finally:
        manager.disconnect(task_id)
        print(f"[WS:{task_id}] Connection closed")
