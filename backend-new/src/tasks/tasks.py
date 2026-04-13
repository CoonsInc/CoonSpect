import json
from redis.asyncio import Redis
from taskiq import TaskiqDepends
from src.infra.taskiq import broker
from src.infra.redis import get_redis
from src.services.stt import STTService, get_stt_service
from src.services.llm import LLMService, get_llm_service
from src.crud.lecture import LectureCRUD, get_lecture_crud
from src.infra.sql.models.lecture import Lecture
from typing import Any
from uuid import UUID
from taskiq.depends.progress_tracker import ProgressTracker, TaskState
from src.services.s3 import S3Service, get_s3_service
from src.tasks.status import TaskStatus

async def update_status(
    tracker: ProgressTracker,
    redis: Redis,
    task_id: str,
    status: TaskStatus,
    data: str | None = None,
    taskiq_state: TaskState = TaskState.STARTED
):
    payload = {
        "status": status,
        "data": data
    }

    await tracker.set_progress(taskiq_state, payload)
    
    payload["task_id"] = task_id
    await redis.publish("task_updates", json.dumps(payload))

@broker.task
async def stt_step(
    bucket: str,
    filename: str,
    stt_service: STTService = TaskiqDepends(get_stt_service)
) -> dict[Any, Any]:
    return await stt_service.transcribe(bucket, filename)

@broker.task
async def llm_step(
    text: str,
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    result = await llm_service.summarize(text)
    return result["summary"]

@broker.task
async def save_step(
    user_id: UUID,
    filename: str,
    filepath: str,
    text: str,
    lecture_crud: LectureCRUD = TaskiqDepends(get_lecture_crud)
) -> Lecture:
    lecture = await lecture_crud.create(Lecture(
        user_id = user_id,
        name = filename,
        audio_url = filepath,
        text = text
    ))

    return lecture

@broker.task
async def run_audio_pipeline(
    task_id: str,
    user_id: UUID,
    bucket: str,
    filename: str,
    s3_service: S3Service = TaskiqDepends(get_s3_service),
    redis: Redis = TaskiqDepends(get_redis),
    tracker: ProgressTracker = TaskiqDepends()
):
    filepath = f"{bucket}/{filename}"
    try:
        await update_status(tracker, redis, task_id, TaskStatus.UPLOADING, filename)
        await s3_service.wait_object(bucket, filename)

        await update_status(tracker, redis, task_id, TaskStatus.STT, filename)
        stt_result = (await (await stt_step.kiq(bucket, filename)).wait_result()).return_value
        
        await update_status(tracker, redis, task_id, TaskStatus.LLM, stt_result["text"])
        summary = (await (await llm_step.kiq(stt_result["text"])).wait_result()).return_value
        
        await update_status(tracker, redis, task_id, TaskStatus.SAVING, summary)
        lecture_id = (await (await save_step.kiq(
            user_id,
            filename,
            filepath,
            summary
        )).wait_result()).return_value

        await update_status(tracker, redis, task_id, TaskStatus.FINISH, lecture_id)
        
    except Exception as e:
        print(f"Error in audio pipeline {e}")
        #await update_status(redis, task_id, "error", str(e))
        raise e
