from src.api.routers.users import router as user_router
from src.api.routers.lectures import router as lecture_router
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from celery import chain
from celery_app import *
from wsmanager import manager
import json

app = FastAPI()


tasks: dict[int, str] = {}


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


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    if task_id in tasks.keys():
        await manager.connect(websocket, task_id)
        await manager.send_message(task_id, json.dumps({"type":"upload_url", "url":"stt-service"}))
        await manager.send_message(task_id, tasks[task_id])
        
        try:
            # Добавляем цикл ожидания сообщений
            while True:
                # Ждем любое сообщение от клиента (можно просто игнорировать содержимое)
                data = await websocket.receive_text()
                print(f"Received from client {task_id}: {data}")
                
        except WebSocketDisconnect:
            print(f"Client {task_id} disconnected")
        except Exception as e:
            print(f"Connection error for task {task_id}: {e}")
        finally:
            manager.disconnect(task_id)
