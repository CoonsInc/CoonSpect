import aioboto3
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from types_aiobotocore_s3 import S3Client
from src.settings import settings

session = aioboto3.Session(
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

@asynccontextmanager
async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    async with session.client('s3', endpoint_url=settings.S3_URL) as s3_client: # type: ignore
        yield s3_client

async def setup_s3():
    """Разовая проверка бакетов при старте"""
    async with get_s3_client() as s3:
        try:
            await s3.head_bucket(Bucket=settings.S3_RAW_LECTURES_BUCKET)
        except Exception:
            await s3.create_bucket(Bucket=settings.S3_RAW_LECTURES_BUCKET)