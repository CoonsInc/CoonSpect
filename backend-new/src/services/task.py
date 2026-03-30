from typing import AsyncGenerator
from uuid import uuid4, UUID
from fastapi import Depends

from src.settings import settings
from src.tasks.tasks import run_audio_pipeline
from src.services.s3 import S3Service, get_s3_service


class TaskService:
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service

    async def run_audio_pipeline(
        self, 
        user_id: UUID, 
        original_filename: str | None, 
        file_content: AsyncGenerator[bytes, None]
    ) -> str:
        """Загружает файл в S3 и запускает фоновую задачу в Taskiq."""
        
        # 1. Формируем имя файла (обрабатываем случай, если имени нет)
        base_name = original_filename or "untitled_lecture"
        filename = f"{uuid4()}_{base_name}"
        bucket = settings.S3_RAW_LECTURES_BUCKET
        
        # 2. Делегируем загрузку S3-сервису через Multipart
        # Теперь TaskService не знает про bucket/key примитивы AWS, 
        # он просто использует готовый контракт!
        await self.s3_service.upload_stream_multipart(
            data_stream=file_content,
            bucket=bucket,
            key=filename
        )
        
        # 3. Запускаем фоновую таску в Taskiq
        task = await run_audio_pipeline.kiq(
            user_id,
            bucket, 
            filename
        )
        
        return task.task_id


def get_task_service(s3_service: S3Service = Depends(get_s3_service)) -> TaskService:
    return TaskService(s3_service)