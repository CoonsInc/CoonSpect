import json
from redis.asyncio import Redis
from taskiq import TaskiqDepends
from loguru import logger
from src.infra.taskiq import broker
from src.infra.redis import get_redis
from src.services.stt import STTService, get_stt_service
from src.services.llm import LLMService, get_llm_service
from src.crud.lecture import LectureCRUD, get_lecture_crud
from src.infra.sql.models.lecture import Lecture
from typing import Any
from uuid import UUID
from src.services.s3 import S3Service, get_s3_service
from src.tasks.status import TaskStatus

async def update_status(
    redis: Redis,
    task_id: str,
    status: TaskStatus,
    data: str | None = None
):
    payload = {
        "status": status,
        "data": data
    }

    await redis.setex(task_id, 43200, json.dumps(payload))
    await redis.publish("task_updates", task_id)

@broker.task(retry_on_error = True)
async def stt_step(
    bucket: str,
    filename: str,
    stt_service: STTService = TaskiqDepends(get_stt_service)
) -> dict[Any, Any]:
    return await stt_service.transcribe(bucket, filename)

@broker.task(retry_on_error = True)
async def llm_step(
    text: str,
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    result = await llm_service.summarize(text)
    return result["summary"]

@broker.task(retry_on_error = True)
async def save_step(
    user_id: UUID,
    filename: str,
    filepath: str,
    text: str,
    lecture_crud: LectureCRUD = TaskiqDepends(get_lecture_crud)
) -> str:
    lecture = await lecture_crud.create(Lecture(
        user_id = user_id,
        name = filename,
        audio_url = filepath,
        text = text
    ))

    return str(lecture.id)

@broker.task
async def run_audio_pipeline(
    task_id: str,
    user_id: UUID,
    bucket: str,
    filename: str,
    redis: Redis = TaskiqDepends(get_redis),
    s3_service: S3Service = TaskiqDepends(get_s3_service)
):
    filepath = f"{bucket}/{filename}"
    try:
        await update_status(redis, task_id, TaskStatus.UPLOADING, filename)
        await s3_service.wait_object(bucket, filename)

        await update_status(redis, task_id, TaskStatus.STT, filepath)
        stt_result = (await (await stt_step.kiq(bucket, filename)).wait_result()).return_value
        
        if not stt_result or "text" not in stt_result:
            await update_status(redis, task_id, TaskStatus.ERROR, "Ошибка: STT сервис не смог обработать аудио")
            logger.error("STT returned empty result or failed")
            return
        
        await update_status(redis, task_id, TaskStatus.LLM, stt_result["text"])
        summary = (await (await llm_step.kiq(stt_result["text"])).wait_result()).return_value
        
        await update_status(redis, task_id, TaskStatus.SAVING, summary)
        lecture_id = (await (await save_step.kiq(
            user_id,
            filename,
            filepath,
            summary
        )).wait_result()).return_value

        await update_status(redis, task_id, TaskStatus.FINISH, lecture_id)
        
    except Exception as e:
        print(f"Error in audio pipeline {e}")
        await update_status(redis, task_id, TaskStatus.ERROR, str(e))
        raise e
