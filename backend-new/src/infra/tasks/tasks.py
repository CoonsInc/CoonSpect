import json
from redis.asyncio import Redis
from httpx import AsyncClient
from taskiq import TaskiqDepends
from uuid import UUID
from src.infra.tasks.broker import broker
from src.infra.sql.session import get_db
from src.infra.http_client import get_http_client
from src.infra.redis import get_redis
from src.services.stt import STTService
from src.services.llm import LLMService
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
    http_client: AsyncClient = TaskiqDepends(get_http_client)
) -> str:
    await update_status(user_id, "stt")
    result = await STTService(http_client).transcribe(bucket, filename)
    return result["text"]

@broker.task
async def llm_step(
    user_id: UUID,
    text: str,
    http_client: AsyncClient = TaskiqDepends(get_http_client)
) -> str:
    await update_status(user_id, "llm")
    result = await LLMService(http_client).summarize(text)
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
async def run_audio_pipeline(user_id: UUID, bucket: str, filename: str):
    try:
        # Шаг 1: Запускаем STT и ждем результат
        # .kiq().get_result() позволяет дождаться выполнения асинхронно
        text = await (await stt_step.kiq(user_id, bucket, filename)).get_result()
        
        # Шаг 2: Передаем текст в LLM
        summary = await (await llm_step.kiq(user_id, text)).get_result()
        
        # Шаг 3: Сохраняем
        await (await save_step.kiq(user_id, summary, filename)).get_result()
        
    except Exception as e:
        await update_status(user_id, "error")
        raise e