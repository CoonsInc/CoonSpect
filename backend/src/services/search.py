# services/search.py
import httpx
from src.settings import settings
from src.infra.http_client import get_http_client

class SearchService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.SEARCH_SERVICE_URL.rstrip("/")
        
    async def search(self, lecture_id: str, query: str) -> dict:
        try:
            response = await self.client.get(
                f"{settings.SEARCH_SERVICE_URL}/search",
                params={"audio_id": lecture_id, "query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Search service error: {e}")
            return {"results": []}

    async def index_lecture(self, lecture_id: str, segments: list) -> None:
        try:
            await self.client.post(
                f"{self.base_url}/index",
                json={"audio_id": lecture_id, "segments": segments}
            )
        except Exception as e:
            logger.warning(f"Search indexing failed for {lecture_id}: {e}")

async def get_search_service() -> SearchService:
    return SearchService(await get_http_client())