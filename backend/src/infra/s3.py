import aioboto3
from typing import AsyncGenerator
from types_aiobotocore_s3 import S3Client
from src.settings import settings

_session = aioboto3.Session(
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    async with _session.client('s3', endpoint_url=settings.S3_URL, region_name="auto") as s3_client: # type: ignore
        yield s3_client

async def setup_s3():
    async with _session.client('s3', endpoint_url=settings.S3_URL, region_name="auto") as s3: # type: ignore
        try:
            await s3.head_bucket(Bucket=settings.S3_RAW_LECTURES_BUCKET)
        except Exception:
            await s3.create_bucket(Bucket=settings.S3_RAW_LECTURES_BUCKET)
