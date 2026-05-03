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
from asyncio import sleep
from src.tasks.tasks import update_status
from src.services.s3 import S3Service, get_s3_service
from src.tasks.status import TaskStatus

@broker.task(retry_on_error = True)
async def stt_step(
    bucket: str,
    filename: str,
    stt_service: STTService = TaskiqDepends(get_stt_service),
) -> dict[Any, Any]:
    await sleep(5)
    return {"text": "hello world"}

@broker.task(retry_on_error = True)
async def llm_step(
    text: str,
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    await sleep(5)
    return f"summarized {text}"

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
