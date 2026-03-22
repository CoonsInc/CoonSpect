import aioboto3
from pathlib import Path
import tempfile

from settings import settings

session = aioboto3.Session(
    aws_access_key_id = settings.S3_ACCESS_KEY,
    aws_secret_access_key = settings.S3_SECRET_KEY,
)

async def get_s3_client():
    async with session.client('s3', endpoint_url = settings.S3_URL) as client:
        yield client

async def download_from_s3(s3_client, bucket: str, filename: str) -> Path:
    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb') as tmp:
        await s3_client.download_fileobj(Bucket=bucket, Key=filename, Fileobj=tmp)
        return Path(tmp.name)
