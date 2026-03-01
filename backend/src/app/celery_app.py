from celery import Celery, chain
from celery.signals import task_prerun
import json
import os
import requests
from pathlib import Path
import uuid

from src.app.db.models.lecture import Lecture
from src.app.db.models.user import User
from src.app.db.session import SessionLocal
from src.app.wsmanager import manager
from src.app.db.redis import redis_sync, redis_async
import src.app.config as config

TASK_MESSAGES = {
    "src.app.celery_app.stt_task": "stt",
    "src.app.celery_app.rag_task": "rag",
    "src.app.celery_app.llm_task": "llm",
    "src.app.celery_app.upload_lecture_task": "saving",
    "src.app.celery_app.finish_task": "finish"
}

DEFAULT_MESSAGE = "unknown"

TASK_FINISH = "src.celery_app.finish_task"

celery = Celery(
    "tasks",
    broker = config.REDIS_URL,
    backend = config.REDIS_URL
)

class ChainException(Exception):
    pass

def send_msg(task_id: str, message: str = DEFAULT_MESSAGE):
    """send task status with some data"""
    redis_sync.publish("ws_events", json.dumps({
        "task_id": task_id,
        "message": message
    }))

def exit_chain(binding, task_id: str, message: str = DEFAULT_MESSAGE):
    """exit from chain with error"""
    send_msg(task_id, "error")
    send_msg(task_id, message)
    manager.disconnect(task_id)

    binding.retry(countdown=0, max_retries=0)

    raise ChainException(message)
    

@celery.task(bind = True)
def stt_task(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "task_id" and "audio_filepath"\n
    writes "data" with stt response
    """
    with open(payload["audio_filepath"], "rb") as audiof:
        response = requests.post(
            config.STT_SERVICE_URL+"/transcribe",
            headers = {"task_id": payload["task_id"]},
            files = {f"file": audiof},
            timeout = 1800
        )
    
    os.remove(payload["audio_filepath"])
    if (response.status_code != 200):
        exit_chain(self, payload["task_id"], f"Error with stt request, status {response.status_code}")

    payload["data"] = response.json()["text"]

    return payload

@celery.task(bind = True)
def stt_task_test(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "task_id" and "audio_filepath"\n
    writes "data" with stt response
    """
    payload["data"] = "hello world"
    return payload

@celery.task(bind = True)
def llm_task(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "task_id" and "data"\n
    writes "data" with llm response
    """

    response = requests.post(
        config.LLM_SERVICE_URL+"/summarize",
        json={"text":payload["data"]},
        timeout = 1800
    )

    if (response.status_code != 200):
        exit_chain(self, payload["task_id"], f"Error with llm request, status {response.status_code}")

    payload["data"] = response.json()["summary"]
    return payload

@celery.task(bind = True)
def llm_task_test(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "task_id" and "data"\n
    writes "data" with llm response
    """
    return payload

@celery.task()
def upload_lecture_task(payload: dict):
    """
    add lecture to user\n
    payload need "task_id", "user_uuid", "data"\n
    writes "data" with lecture id
    """

    with SessionLocal() as db:
        lecture = Lecture(
            user_id=payload["user_uuid"],
            audio_url=payload["audio_filepath"],
            text=payload["data"],
        )
        db.add(lecture)
        db.commit()
        db.refresh(lecture)

        text_path = Path(f"{lecture.id}.txt").resolve()
        with open(text_path, "w") as f:
            f.write(payload["data"])
        
        lecture.audio_url = str(text_path)
        db.commit()

        lecture_id = lecture.id

    payload["data"] = str(lecture_id)
    return payload

@celery.task()
def finish_task(payload: dict):
    """
    send payload["data"] as message in websocket and close connection\n
    payload need "task_id", "data"
    """
    send_msg(payload["task_id"], payload["data"])
    manager.disconnect(payload["task_id"])

@task_prerun.connect
def track_task(task_id=None, task=None, sender=None, **kwargs):
    status = TASK_MESSAGES.get(sender.name, DEFAULT_MESSAGE)
    task_id = kwargs["args"][0]["task_id"]
    redis_sync.set(f"task:{task_id}", status)
    send_msg(kwargs["args"][0]["task_id"], status)

def run_audio_pipeline(task_id: str, user_uuid: uuid.UUID, audio_filepath: str):
    if not manager.contains(task_id):
        raise Exception(f"task_id {task_id} not found")
    
    with SessionLocal() as db:
        db.query(User).filter()

    if not os.path.exists(audio_filepath):
        raise Exception(f"File {audio_filepath} not found")

    print(f"[AUDIO PIPELINE] task_id: {task_id}; user_uuid {user_uuid}; audio_filepath {audio_filepath}")

    initial_payload = {
        "task_id": task_id,
        "audio_filepath": audio_filepath,
        "user_uuid": user_uuid
    }

    chain(
        stt_task.s(initial_payload),
        llm_task.s(),
        upload_lecture_task.s(),
        finish_task.s()
    ).apply_async()

def run_audio_pipeline_test(task_id: str, audio_filepath: str):
    if not manager.contains(task_id):
        raise Exception(f"task_id {task_id} not found")
    
    user = User(
        id = uuid.uuid4(),
        username = str(uuid.uuid4()),
        password_hash = str(uuid.uuid4())
    )

    with SessionLocal() as db:
        db.add(user)
        db.commit()
        db.refresh(user)

    if not os.path.exists(audio_filepath):
        raise Exception(f"File {audio_filepath} not found")

    print(f"[AUDIO PIPELINE] task_id: {task_id}; user_uuid {str(user.id)}; audio_filepath {audio_filepath}")

    initial_payload = {
        "task_id": task_id,
        "audio_filepath": audio_filepath,
        "user_uuid": user.id
    }

    chain(
        stt_task.s(initial_payload),
        llm_task.s(),
        upload_lecture_task.s(),
        finish_task.s()
    ).apply_async()

async def ws_event_listener():
    pubsub = redis_async.pubsub()
    await pubsub.subscribe("ws_events")
    async for message in pubsub.listen():
        print(f"Redis received: {message}")
        if message["type"] == "message":
            data = json.loads(message["data"])
            print(f"Forwarding to WS: {data}")
            await manager.send_message(data["task_id"], data["message"])
