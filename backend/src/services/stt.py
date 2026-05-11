from fastapi import Depends
from httpx import AsyncClient

from src.infra.http_client import get_http_client
from src.settings import settings


class STTService:
    def __init__(self, http_client: AsyncClient):
        self._client = http_client
        self._base_url = settings.STT_SERVICE_URL.rstrip("/")

    async def transcribe(self, bucket: str, filename: str) -> dict:
        url = f"{self._base_url}/transcribe"
        payload = {"bucket": bucket, "filename": filename}

        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def get_stt_service(http_client: AsyncClient = Depends(get_http_client)) -> STTService:
    return STTService(http_client)
