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
from loguru import logger

async def update_status(
    task_id: str,
    status: str,
    data: str | None = None,
    redis: Redis = TaskiqDepends(get_redis)
):
    await redis.set(f"task:{task_id}", status)
    payload = {
        "task_id": task_id,
        "status": status,
        "data": data
    }
    await redis.publish("task_updates", json.dumps(payload))

@broker.task
async def stt_step(
    task_id: str,
    bucket: str,
    filename: str,
    stt_service: STTService = TaskiqDepends(get_stt_service)
) -> dict[Any, Any]:
    await update_status(task_id, "stt", filename)
    return await stt_service.transcribe(bucket, filename)

@broker.task
async def llm_step(
    task_id: str,
    text: str,
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    await update_status(task_id, "llm", text)
    result = await llm_service.summarize(text)
    return result["summary"]

@broker.task
async def save_step(
    task_id: str,
    user_id: UUID,
    filename: str,
    filepath: str,
    text: str,
    lecture_crud: LectureCRUD = TaskiqDepends(get_lecture_crud)
) -> Lecture:
    await update_status(task_id, "saving")
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
    filename: str
):
    filepath = f"{bucket}/{filename}"
    try:
        stt_result = await (await stt_step.kiq(task_id, bucket, filename)).get_result()
        
        summary = await (await llm_step.kiq(task_id, stt_result["text"])).get_result()
        
        lecture= await (await save_step.kiq(
            task_id,
            user_id,
            filename,
            filepath,
            summary,
        )).get_result()

        await update_status(task_id, "finish", str(lecture.id))
        
    except Exception as e:
        logger.exception("Error in audio pipeline")
        await update_status(task_id, "error", str(e))
        raise e
