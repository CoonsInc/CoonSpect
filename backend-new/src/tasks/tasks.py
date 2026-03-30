import json
from redis.asyncio import Redis
from taskiq import TaskiqDepends
from uuid import UUID
from src.infra.taskiq import broker
from src.infra.sql.session import get_db
from src.infra.redis import get_redis
from src.services.stt import STTService, get_stt_service
from src.services.llm import LLMService, get_llm_service
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.lecture import LectureCRUD

async def update_status(
    user_id: UUID,
    status: str,
    redis: Redis = TaskiqDepends(get_redis)
):
    await redis.set(f"task:{user_id}", status)
    await redis.publish(f"ws:{user_id}", json.dumps({"status": status}))

@broker.task
async def stt_step(
    user_id: UUID,
    bucket: str,
    filename: str,
    stt_service: STTService = TaskiqDepends(get_stt_service)
) -> str:
    await update_status(user_id, "stt")
    result = await stt_service.transcribe(bucket, filename)
    return result["text"]

@broker.task
async def llm_step(
    user_id: UUID,
    text: str,
    llm_service: LLMService = TaskiqDepends(get_llm_service)
) -> str:
    await update_status(user_id, "llm")
    result = await llm_service.summarize(text)
    return result["summary"]

@broker.task
async def save_step(
    user_id: UUID,
    data: str,
    filename: str,
    db: AsyncSession = TaskiqDepends(get_db)
):
    lecture_crud = LectureCRUD(db)
    await update_status(user_id, "saving")
    # Логика записи в БД...
    await update_status(user_id, "finish")

@broker.task
async def run_audio_pipeline(
    user_id: UUID,
    bucket: str,
    filename: str
):
    try:
        text = await (await stt_step.kiq(user_id, bucket, filename)).get_result()
        
        summary = await (await llm_step.kiq(user_id, text)).get_result()
        
        await (await save_step.kiq(user_id, summary, filename)).get_result()
        
    except Exception as e:
        await update_status(user_id, "error")
        raise e
