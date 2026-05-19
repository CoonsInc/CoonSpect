from fastapi import APIRouter, Depends
from uuid import UUID

from src.services.search import SearchService, get_search_service

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/{lecture_id}")
async def search(
    lecture_id: UUID,
    query: str,
    service: SearchService = Depends(get_search_service)
):
    return await service.search(lecture_id, query)