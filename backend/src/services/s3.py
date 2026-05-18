from fastapi import Depends
from types_aiobotocore_s3 import S3Client

from src.infra.s3 import get_s3_client


class S3Service:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    async def wait_object(
        self, bucket: str, key: str, delay: int = 5, max_attempts: int = 20
    ) -> None:
        waiter = self.s3_client.get_waiter("object_exists")
        await waiter.wait(
            Bucket=bucket,
            Key=key,
            WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts},
        )

    async def get_download_url(
        self, bucket: str, key: str, expiration: int = 3600
    ) -> str:
        return await self.s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expiration
        )

    async def get_upload_url(
        self, bucket: str, key: str, content_type: str, expiration: int = 3600
    ) -> str:
        return await self.s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expiration,
        )

    async def delete(self, bucket: str, key: str) -> None:
        await self.s3_client.delete_object(Bucket=bucket, Key=key)


def get_s3_service(s3_client: S3Client = Depends(get_s3_client)) -> S3Service:
    return S3Service(s3_client)
