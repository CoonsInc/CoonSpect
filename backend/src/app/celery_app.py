from celery import Celery
from celery.signals import task_prerun
import json
import requests
import time
from pydantic import BaseModel

from src.app.settings import settings
from src.app.clients.sql.session import SessionLocal
from src.app.clients.sql.models import Lecture
from src.app.wsmanager import manager
from src.app.clients.redis import redis_sync

TASK_MESSAGES = {
    "src.app.celery_app.stt_task": "stt",
    "src.app.celery_app.rag_task": "rag",
    "src.app.celery_app.llm_task": "llm",
    "src.app.celery_app.upload_lecture_task": "saving",
    "src.app.celery_app.finish_task": "finish",
    
    "src.app.celery_app.stt_task_test": "stt",
    "src.app.celery_app.rag_task_test": "rag",
    "src.app.celery_app.llm_task_test": "llm"
}

DEFAULT_MESSAGE = "unknown"

TASK_FINISH = "src.celery_app.finish_task"

celery = Celery(
    "tasks",
    broker = settings.REDIS_URL,
    backend = settings.REDIS_URL
)

class ChainException(Exception):
    pass

class RequestTranscribeSTT(BaseModel):
    bucket: str = ""
    filename: str = ""

def send_msg(user_id: str, message: str = DEFAULT_MESSAGE):
    """send task status with some data"""
    redis_sync.publish("ws_events", json.dumps({
        "user_id": user_id,
        "message": message
    }))

def exit_chain(binding, user_id: str, message: str = DEFAULT_MESSAGE):
    """exit from chain with error"""
    send_msg(user_id, "error")
    send_msg(user_id, message)
    manager.disconnect(user_id)

    binding.retry(countdown=0, max_retries=0)

    raise ChainException(message)

@task_prerun.connect
def track_task(user_id=None, task=None, sender=None, **kwargs):
    status = TASK_MESSAGES.get(sender.name, DEFAULT_MESSAGE)
    user_id = kwargs["args"][0]["user_id"]
    redis_sync.set(f"task:{user_id}", status)
    send_msg(user_id, status)

@celery.task(bind = True)
def stt_task(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "user_id", "bucket", "filename"\n
    writes "data" with stt response
    """
    try:
        response = requests.post(
            settings.STT_SERVICE_URL+"/transcribe",
            json = RequestTranscribeSTT(bucket = payload["bucket"], filename = payload["filename"]).model_dump(),
            timeout = 1800
        )
    except requests.exceptions.ConnectionError as e:
        print(f"[STT PIPELINE] suspicious error: {e}")
        exit_chain(self, payload["user_id"], e)
    
    if response.status_code != 200:
        print(f"[STT PIPELINE] suspicious response from stt: {response.text}")
        exit_chain(self, payload["user_id"], f"Error with stt request, status {response.status_code}")

    payload["data"] = response.json()["text"]

    return payload

@celery.task(bind = True)
def llm_task(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "user_id" and "data"\n
    writes "data" with llm response
    """

    response = requests.post(
        settings.LLM_SERVICE_URL+"/summarize",
        json={"text":payload["data"]},
        timeout = 1800
    )

    if (response.status_code != 200):
        exit_chain(self, payload["user_id"], f"Error with llm request, status {response.status_code}")

    payload["data"] = response.json()["summary"]
    return payload

@celery.task()
def upload_lecture_task(payload: dict):
    """
    add lecture to user\n
    payload need "user_id", "user_uuid", "data"\n
    writes "data" with lecture id
    """

    with SessionLocal() as db:
        lecture = Lecture(
            user_id=payload["user_id"],
            audio_url=f"{payload["bucket"]}/{payload["filename"]}",
            text=payload["data"],
        )
        db.add(lecture)
        db.commit()
        db.refresh(lecture)
        db.commit()

        lecture_id = lecture.id

    payload["data"] = str(lecture_id)
    return payload

@celery.task()
def finish_task(payload: dict):
    """
    send payload["data"] as message in websocket and close connection\n
    payload need "user_id", "data"
    """
    send_msg(payload["user_id"], payload["data"])
    manager.disconnect(payload["user_id"])




@celery.task(bind = True)
def stt_task_test(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "user_id" and "audio_filepath"\n
    writes "data" with stt response
    """
    time.sleep(2)
    payload["data"] = "hello world"
    return payload

@celery.task(bind = True)
def llm_task_test(self, payload: dict):
    """
    send audio file to stt service\n
    payload need "user_id" and "data"\n
    writes "data" with llm response
    """
    time.sleep(2)
    return payload
