from typing import AsyncGenerator
from uuid import uuid4
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from taskiq import AsyncTaskiqTask

from src.settings import settings
from src.tasks.tasks import run_audio_pipeline
from src.tasks.tasks_mock import run_audio_pipeline as run_audio_pipeline_mock
from src.services.s3 import S3Service, get_s3_service
from src.infra.redis import get_redis
from src.infra.sql.models.user import User
from src.tasks import tasks
from typing import Any
from uuid import UUID
from loguru import logger

class TaskService:
    def __init__(self, s3_service: S3Service, redis: Redis):
        self.s3_service = s3_service
        self.redis = redis

    async def start(self, user: User, original_filename: str | None, file_content: AsyncGenerator[bytes, None]) -> str:
        task_id = self.get_task_id(user)
        if await self.redis.get(task_id):
            raise HTTPException(400, "User already have task in progress")
        await tasks.update_status(self.redis, task_id, "uploading", original_filename)
        await self.run_audio_pipeline(task_id, user.id, original_filename, file_content)

        return task_id

    async def run_audio_pipeline(
        self, 
        task_id: str,
        user_id: UUID,
        original_filename: str | None, 
        file_content: AsyncGenerator[bytes, None]
    ) -> AsyncTaskiqTask[Any]:
        """Загружает файл в S3 и запускает фоновую задачу в Taskiq."""
        base_name = original_filename or "untitled_lecture"
        filename = f"{uuid4()}_{base_name}"
        bucket = settings.S3_RAW_LECTURES_BUCKET
        
        logger.debug("UPLOADING")
        
        await self.s3_service.upload_stream_multipart(
            data_stream=file_content,
            bucket=bucket,
            key=filename
        )

        logger.debug("UPLOADED")
        
        if settings.BACKEND_MODE == "prod":
            logger.debug("PROD PIPELINE")
            return await run_audio_pipeline.kiq(
                task_id,
                user_id,
                bucket, 
                filename
            )
        else:
            logger.debug("MOCK PIPELINE")
            return await run_audio_pipeline_mock.kiq(
                task_id,
                user_id,
                bucket, 
                filename
            )
    
    def get_task_id(self, user: User) -> str:
        return f"task:{user.id}"
    
    async def get_task_status(self, task_id: str) -> str | None:
        return await self.redis.get(task_id)



def get_task_service(s3_service: S3Service = Depends(get_s3_service), redis: Redis = Depends(get_redis)) -> TaskService:
    return TaskService(s3_service, redis)
