from uuid import uuid4
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from typing import Any
from uuid import UUID
from loguru import logger
import json

from src.settings import settings
from src.tasks.tasks import run_audio_pipeline
from src.tasks.tasks_mock import run_audio_pipeline as run_audio_pipeline_mock
from src.services.s3 import S3Service, get_s3_service
from src.infra.redis import get_redis
from src.infra.sql.models.user import User
from src.tasks.tasks import update_status
from src.tasks.status import TaskStatus
from src.api.schemas.task import TaskInit

class TaskService:
    def __init__(self, s3_service: S3Service, redis: Redis):
        self.s3_service = s3_service
        self.redis = redis

    async def start(self, user: User) -> TaskInit:
        task_id = self.get_task_id(user)
        status = await self.get_task_status(task_id)
        if status:
            msg = f"User {user.id} have task in progress {status}"
            logger.warning(msg)
            raise HTTPException(400, msg)
        upload_url = await self.run_audio_pipeline(task_id, user.id)

        return TaskInit(task_id = task_id, upload_url = upload_url)
    
    async def ws_start(self, task_id: str) -> str | None:
        task_status = await self.get_task_status(task_id)

        if not task_status or TaskStatus(task_status["status"]).is_final:
            logger.warning(f"Trying to track empty task {task_id}")
            await self.redis.delete(task_id)
            return None
        
        return json.dumps(obj=task_status)

    async def run_audio_pipeline(
        self, 
        task_id: str,
        user_id: UUID
    ) -> str:
        """Загружает файл в S3 и запускает фоновую задачу в Taskiq."""
        filename = str(uuid4())
        bucket = settings.S3_RAW_LECTURES_BUCKET

        upload_url = await self.s3_service.get_upload_url(bucket, filename, "audio/mpeg", 21600)
        
        if settings.BACKEND_MODE == "prod":
            logger.debug("PROD PIPELINE")
            await run_audio_pipeline.kiq(
                task_id,
                user_id,
                bucket, 
                filename
            )
        else:
            logger.debug("MOCK PIPELINE")
            await run_audio_pipeline_mock.kiq(
                task_id,
                user_id,
                bucket, 
                filename
            )
        
        await update_status(self.redis, task_id, TaskStatus.STARTING)

        return upload_url
    
    def get_task_id(self, user: User) -> str:
        return f"task:{user.id}"
    
    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        status_encoded: str = await self.redis.get(task_id)
        if status_encoded is not None:
            status_decoded: dict[str, Any] = json.loads(status_encoded)
            if not TaskStatus(status_decoded["status"]).is_final:
                return status_decoded
        return None

def get_task_service(s3_service: S3Service = Depends(get_s3_service), redis: Redis = Depends(get_redis)) -> TaskService:
    return TaskService(s3_service, redis)
