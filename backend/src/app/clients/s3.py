import aioboto3
from src.app.config import S3_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_RAW_LECTURES_BUCKET

session = aioboto3.Session(
    aws_access_key_id = S3_ACCESS_KEY,
    aws_secret_access_key = S3_SECRET_KEY,
)

async def create_buckets_if_not_exists():
    async with session.client('s3', endpoint_url = S3_URL) as s3_client:
        try:
            await s3_client.head_bucket(Bucket=S3_RAW_LECTURES_BUCKET)
        except s3_client.exceptions.ClientError:
            await s3_client.create_bucket(Bucket=S3_RAW_LECTURES_BUCKET)

async def get_s3_client():
    async with session.client('s3', endpoint_url = S3_URL) as client:
        yield client