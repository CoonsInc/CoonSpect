from uuid import UUID
from celery import chain

from src.app.celery_app import *
from src.app.clients.redis import redis_async as r

def run_audio_pipeline(user_id: UUID, audio_filepath: str):    
    if not os.path.exists(audio_filepath):
        raise Exception(f"File {audio_filepath} not found")

    print(f"[AUDIO PIPELINE] user_id = {user_id}; audio_filepath = {audio_filepath}")

    initial_payload = {
        "user_id": str(user_id),
        "audio_filepath": audio_filepath,
    }

    chain(
        stt_task.s(initial_payload),
        llm_task.s(),
        upload_lecture_task.s(),
        finish_task.s()
    ).apply_async()

def run_audio_pipeline_test(user_id: UUID, audio_filepath: str):
    if not os.path.exists(audio_filepath):
        raise Exception(f"File {audio_filepath} not found")

    print(f"[AUDIO PIPELINE] task_id: {user_id}; audio_filepath {audio_filepath}")

    initial_payload = {
        "user_id": str(user_id),
        "audio_filepath": audio_filepath
    }

    chain(
        stt_task_test.s(initial_payload),
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
            print(f"!!! Forwarding to WS: {data}")
            await manager.send_message(data["task_id"], data["message"])

            
