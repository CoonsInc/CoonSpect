from fastapi import Depends
from typing import AsyncGenerator, List
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_s3.type_defs import (
    CompletedPartTypeDef, 
    CompletedMultipartUploadTypeDef
)
from src.infra.s3 import get_s3_client

class S3Service:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client
        self.min_part_size = 5 * 1024 * 1024  # 5 MB

    async def wait_object(self, bucket: str, key: str):
        waiter = self.s3_client.get_waiter("object_exists")
        await waiter.wait(Bucket=bucket, Key=key)

    async def upload_stream_multipart(
        self,
        data_stream: AsyncGenerator[bytes, None],
        bucket: str,
        key: str
    ) -> None:
        """Безопасно загружает данные из генератора в S3 через Multipart."""
                # 1. Инициализация
        mp = await self.s3_client.create_multipart_upload(Bucket=bucket, Key=key)
        upload_id = mp["UploadId"]
        
        parts: List[CompletedPartTypeDef] = []
        part_number = 1
        buffer = b""
        
        try:
            # 2. Читаем и буферизуем
            async for chunk in data_stream:
                buffer += chunk
                
                if len(buffer) >= self.min_part_size:
                    part = await self.s3_client.upload_part(
                        Bucket=bucket,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=buffer
                    )
                    parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                    buffer = b""
                    part_number += 1
            
            # 3. Последний кусочек
            if buffer:
                part = await self.s3_client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=buffer
                )
                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
            
            # 4. Завершение
            if not parts:
                await self.s3_client.abort_multipart_upload(
                    Bucket=bucket, Key=key, UploadId=upload_id
                )
                await self.s3_client.put_object(Bucket=bucket, Key=key, Body=b"")
            
            multipart_mapping = CompletedMultipartUploadTypeDef(Parts=parts)

            await self.s3_client.complete_multipart_upload(
                Bucket = bucket,
                Key = key,
                UploadId = upload_id,
                MultipartUpload = multipart_mapping
            )
            
        except Exception as e:
            # 5. Отмена при ошибке
            await self.s3_client.abort_multipart_upload(
                Bucket=bucket, Key=key, UploadId=upload_id
            )
            raise e

def get_s3_service(s3_client: S3Client = Depends(get_s3_client)) -> S3Service:
    return S3Service(s3_client)