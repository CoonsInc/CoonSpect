from uuid import UUID
from celery import chain

from src.app.celery_app import *
from src.app.clients.redis import redis_async as r

def run_audio_pipeline(user_id: UUID, bucket: str, filename: str):
    print(f"[AUDIO PIPELINE] user_id = {user_id}; bucket {bucket}; filename {filename}")

    initial_payload = {
        "user_id": str(user_id),
        "bucket": bucket,
        "filename": filename
    }

    chain(
        stt_task.s(initial_payload),
        llm_task.s(),
        upload_lecture_task.s(),
        finish_task.s()
    ).apply_async()

def run_audio_pipeline_test(user_id: UUID, bucket: str, filename: str):
    print(f"[AUDIO PIPELINE] task_id: {user_id}; bucket {bucket}; filename {filename}")
    
    initial_payload = {
        "user_id": str(user_id),
        "bucket": bucket,
        "filename": filename
    }

    chain(
        stt_task.s(initial_payload),
        llm_task_test.s(),
        upload_lecture_task.s(),
        finish_task.s()
    ).apply_async()

async def ws_event_listener():
    pubsub = r.pubsub()
    await pubsub.subscribe("ws_events")
    async for message in pubsub.listen():
        print(f"Redis received: {message}")
        if message["type"] == "message":
            data = json.loads(message["data"])
            await manager.send_message(data["user_id"], data["message"])

            
