from fastapi import Depends
from httpx import AsyncClient
from src.infra.http_client import get_http_client
from src.settings import settings

class LLMService:
    def __init__(self, http_client: AsyncClient):
        self._client = http_client
        self._base_url = settings.LLM_SERVICE_URL.rstrip("/")

    async def summarize(self, text: str) -> dict:
        url = f"{self._base_url}/summarize"
        
        response = await self._client.post(url, json={"text": text})
        response.raise_for_status()
        return response.json()
    
def get_llm_service(http_client: AsyncClient = Depends(get_http_client)) -> LLMService:
    return LLMService(http_client)
