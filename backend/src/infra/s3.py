import asyncio
from collections.abc import AsyncGenerator

import aioboto3
from botocore.exceptions import ClientError
from loguru import logger
from types_aiobotocore_s3 import S3Client

from src.settings import settings

_session = aioboto3.Session(
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

async def _sync_example_bucket(s3: S3Client) -> None:
    local_dir = settings.EXAMPLES_DIR
    if not local_dir.exists():
        logger.warning(f"Examples directory not found: {local_dir}")
        return

    allowed_files = {task.filename for task in settings.LECTURES_EXAMPLE}
    if not allowed_files:
        logger.warning(f"No example tasks found in {settings.EXAMPLES_JSON}")
        return

    bucket = settings.S3_RAW_LECTURES_EXAMPLE_BUCKET

    local_files: dict[str, int] = {}
    for filename in allowed_files:
        file_path = local_dir / filename
        if file_path.is_file():
            local_files[filename] = file_path.stat().st_size
        else:
            logger.warning(f"Example file not found locally: {filename}")

    s3_files: dict[str, int] = {}
    async for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            s3_files[obj["Key"]] = obj["Size"]

    to_delete = [key for key in s3_files if key not in local_files]
    if to_delete:
        await s3.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": k} for k in to_delete]}
        )
        logger.info(f"Deleted {len(to_delete)} obsolete files from S3")

    to_upload = [k for k, size in local_files.items() if s3_files.get(k) != size]
    if to_upload:
        tasks = [
            s3.upload_file(
                Filename=str(local_dir / key),
                Bucket=bucket,
                Key=key,
                ExtraArgs={"ContentType": "application/octet-stream"}
            )
            for key in to_upload
        ]
        await asyncio.gather(*tasks)
        logger.info(f"Uploaded/updated {len(to_upload)} files to S3")
    else:
        logger.info("S3 example bucket is already up to date")


async def setup_s3() -> None:
    async with _session.client(
        "s3", endpoint_url=settings.S3_URL, region_name="us-east-1" # type: ignore
    ) as s3:
        buckets = (
            settings.S3_RAW_LECTURES_BUCKET,
            settings.S3_RAW_LECTURES_EXAMPLE_BUCKET
        )
        
        for bucket in buckets:
            try:
                await s3.create_bucket(Bucket=bucket)
                logger.info(f"Created bucket: {bucket}")
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                    logger.debug(f"Bucket {bucket} already exists")
                else:
                    raise

        await _sync_example_bucket(s3)

async def get_s3_client() -> AsyncGenerator[S3Client]:
    async with _session.client(
        "s3", endpoint_url=settings.S3_URL, region_name="auto"
    ) as s3: # type: ignore
        yield s3
    