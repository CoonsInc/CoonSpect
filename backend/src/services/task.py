import json
import os
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from loguru import logger
from redis.asyncio import Redis

from src.api.schemas.task import ExampleTaskDescription, ExampleTaskInit, TaskInit
from src.infra.db.models.user import User
from src.infra.redis import get_redis
from src.services.s3 import S3Service, get_s3_service
from src.settings import Environment, settings
from src.tasks.status import TaskStatus
from src.tasks.tasks import run_audio_pipeline, update_status
from src.tasks.tasks_mock import run_audio_pipeline as run_audio_pipeline_mock


class TaskService:
    def __init__(self, s3_service: S3Service, redis: Redis):
        self.s3_service = s3_service
        self.redis = redis

    async def start(self, user: User, original_filename: str) -> TaskInit:
        task_id = self.get_task_id(user)
        await self.check_task_dont_exist(user.id, task_id)

        upload_url = await self.get_upload_url(task_id, original_filename)
        return TaskInit(task_id=task_id, upload_url=upload_url)

    async def ws_start(self, task_id: str) -> str | None:
        task_status = await self.get_task_status(task_id)

        if not task_status or TaskStatus(task_status["status"]).is_final:
            logger.warning(f"Trying to track empty task {task_id}")
            await self.redis.delete(task_id)
            return None

        return json.dumps(obj=task_status)

    async def get_upload_url(self, task_id: str, original_filename: str) -> str:
        ext = os.path.splitext(original_filename.lower())[1]

        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file extension: {ext}")

        filename = f"{uuid4()}{ext}"
        bucket = settings.S3_RAW_LECTURES_BUCKET

        await self.redis.set(f"{task_id}:filename", filename, ex=3600)

        upload_url = await self.s3_service.get_upload_url(
            bucket, filename, "audio/mpeg", 21600
        )

        await update_status(self.redis, task_id, TaskStatus.STARTING)
        return upload_url

    async def confirm_upload_and_start(self, task_id: str, user_id: UUID) -> None:
        """Запускает воркер после подтверждения загрузки фронтендом."""
        bucket = settings.S3_RAW_LECTURES_BUCKET
        filename: str = await self.redis.get(f"{task_id}:filename")
        if not filename:
            raise HTTPException(400, "Upload session expired or not found")

        await self.run_audio_pipeline(task_id, user_id, bucket, filename)

    async def start_example(self, user: User, filename: str) -> ExampleTaskInit:
        bucket = settings.S3_RAW_LECTURES_EXAMPLE_BUCKET
        
        found = False
        for lecture_example in settings.LECTURES_EXAMPLE:
            found = lecture_example.filename == filename
            if found:
                break
        if not found:
            raise HTTPException(400, f"Unknown example {filename}")
        
        task_id = self.get_task_id(user)
        await self.check_task_dont_exist(user.id, task_id)

        await update_status(self.redis, task_id, TaskStatus.STARTING)
        await self.run_audio_pipeline(task_id, user.id, bucket, filename)
        return ExampleTaskInit(task_id=task_id)
    
    def example_list(self) -> list[ExampleTaskDescription]:
        return settings.LECTURES_EXAMPLE

    async def run_audio_pipeline(
        self,
        task_id: str,
        user_id: UUID,
        bucket: str,
        filename: str
    ) -> None:
        if settings.ENVIRONMENT == Environment.MOCK:
            logger.debug("MOCK PIPELINE")
            await run_audio_pipeline_mock.kiq(task_id, user_id, bucket, filename)
        else:
            await run_audio_pipeline.kiq(task_id, user_id, bucket, filename)

    async def check_task_dont_exist(self, user_id: UUID, task_id: str) -> None:
        status = await self.get_task_status(task_id)
        if status:
            msg = f"User {user_id} have task in progress {status}"
            logger.warning(msg)
            raise HTTPException(400, msg)

    def get_task_id(self, user: User) -> str:
        return f"task:{user.id}"

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        status_encoded: str = await self.redis.get(task_id)
        if status_encoded is not None:
            status_decoded: dict[str, Any] = json.loads(status_encoded)
            if not TaskStatus(status_decoded["status"]).is_final:
                return status_decoded
        return None


def get_task_service(
    s3_service: S3Service = Depends(get_s3_service), redis: Redis = Depends(get_redis)
) -> TaskService:
    return TaskService(s3_service, redis)
