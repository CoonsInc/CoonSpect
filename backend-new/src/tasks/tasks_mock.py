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
from asyncio import sleep
from src.tasks.tasks import update_status
from taskiq.depends.progress_tracker import ProgressTracker, TaskProgress

@broker.task
async def stt_step(
    task_id: str,
    bucket: str,
    filename: str,
    redis: Redis = TaskiqDepends(get_redis),
    stt_service: STTService = TaskiqDepends(get_stt_service)
) -> dict[Any, Any]:
    await update_status(redis, task_id, "stt", filename)
    await sleep(5)
    return {"text": "hello world"}

@broker.task
async def llm_step(
    task_id: str,
    text: str,
    redis: Redis = TaskiqDepends(get_redis),
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    await update_status(redis, task_id, "llm", text)
    await sleep(5)
    return f"summarized {text}"

@broker.task
async def save_step(
    task_id: str,
    user_id: UUID,
    filename: str,
    filepath: str,
    text: str,
    redis: Redis = TaskiqDepends(get_redis),
    lecture_crud: LectureCRUD = TaskiqDepends(get_lecture_crud)
) -> str:
    await update_status(redis, task_id, "saving")
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
    tracker: ProgressTracker = TaskiqDepends()
):
    filepath = f"{bucket}/{filename}"
    try:
        logger.info("some stt")
        stt_result = (await (await stt_step.kiq(task_id, bucket, filename)).wait_result()).return_value
        
        logger.info("some llm")
        summary = (await (await llm_step.kiq(task_id, stt_result["text"])).wait_result()).return_value
        
        logger.info("some db")
        lecture_id = (await (await save_step.kiq(
            task_id,
            user_id,
            filename,
            filepath,
            summary
        )).wait_result()).return_value

        print("done")
        await update_status(redis, task_id, "finish", lecture_id)
        
    except Exception as e:
        logger.exception("Error in audio pipeline")
        await update_status(redis, task_id, "error", str(e))
        raise e
