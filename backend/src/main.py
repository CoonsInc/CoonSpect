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
    return {"status": "ok"}


app.include_router(user_router)
app.include_router(lecture_router)

@app.get("/create_task")
def create_task():
    task_id: int = 0
    if (len(tasks.keys()) == 0):
        tasks[0] = "uploading"
    else:
        task_id = max(tasks.keys())+1
        tasks[task_id] = "uploading"

    return {"task_id": task_id}


@app.get("/correct_task_id/{task_id}")
async def check_task_id(task_id: int, sender: str = None):
    if (task_id in tasks.keys()):
        if (sender == "stt"):
            tasks[task_id] = "stt"
            await manager.send_message(task_id, "stt")
        elif (sender == "rag"):
            tasks[task_id] = "rag"
            await manager.send_message(task_id, "rag")
        elif (sender == "llm"):
            tasks[task_id] = "llm"
            await manager.send_message(task_id, "llm")

        return {"status":"correct"}
    return {"status":"incorrect"}


@app.post("/finish")
async def finish(content: dict):
    if (tasks.get(content["task_id"]) == None):
        return {"status":"unsuccess"}
    
    tasks.pop(content["task_id"])
    tasks_result[content["task_id"]] = content["content"]
    await manager.send_message(content["task_id"], "finish")
    return {"status":"success"}
    


@app.post("/result/{task_id}")
async def finish(task_id: int):
    if (tasks_result.get(task_id) == None):
        return {"exist":False, "content":None}
    
    return {"exist":True, "content":tasks_result[task_id]}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    if task_id not in tasks:
        await websocket.close(code=4000)
        return

    await manager.connect(websocket, task_id)
    await manager.send_message(task_id, tasks[task_id])

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client {task_id}: {data}")

            try:
                payload = json.loads(data)
            except Exception as e:
                print(f"Invalid JSON from client: {e}")
                continue

            # --- Обрабатываем тип сообщения ---
            if payload.get("type") == "file":
                filename = payload.get("filename", f"task_{task_id}.wav")
                content_b64 = payload.get("content")

                if not content_b64:
                    await manager.send_message(task_id, "error: no content")
                    continue

                # --- Сохраняем временный файл ---
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                    audio_bytes = base64.b64decode(content_b64)
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name

                # --- Отправляем файл на STT сервис ---
                await manager.send_message(task_id, "stt")
                try:
                    async with aiohttp.ClientSession() as session:
                        with open(tmp_path, "rb") as f:
                            form = aiohttp.FormData()
                            form.add_field("file", f, filename=filename, content_type="audio/wav")

                            async with session.post("http://stt-service:8000/transcribe", data=form) as resp:
                                if resp.status != 200:
                                    await manager.send_message(task_id, f"error: stt failed {resp.status}")
                                    continue

                                stt_result = await resp.json()
                                text = stt_result.get("text", "")
                                tasks_result[task_id] = text

                                await manager.send_message(task_id, "finish")

                except Exception as e:
                    print(f"STT error for task {task_id}: {e}")
                    await manager.send_message(task_id, f"error: {e}")

                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            else:
                print(f"Unknown message type from {task_id}: {payload.get('type')}")

    except WebSocketDisconnect:
        print(f"Client {task_id} disconnected")
    finally:
        manager.disconnect(task_id)