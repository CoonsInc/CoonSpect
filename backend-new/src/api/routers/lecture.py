from fastapi import APIRouter, Depends
from uuid import UUID

from src.api.schemas.lecture import LectureRead, LectureUpdate, LecturesPage
from src.services.lecture import LectureService, get_lecture_service
from src.infra.sql.models.user import User
from src.services.auth import authenticate
from src.api.schemas.status import Status

router = APIRouter(prefix="/lecture", tags=["lecture"])

@router.get("/list", response_model=LecturesPage)
async def get_list(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    user_id: UUID | None = None,
    service: LectureService = Depends(get_lecture_service)
):
    return await service.get_lectures_page(
        page=page, limit=limit, sort_by=sort_by, order=order, user_id=user_id
    )

@router.get("/{lecture_id}", response_model=LectureRead)
async def get(
    lecture_id: UUID,
    service: LectureService = Depends(get_lecture_service)
):
    return await service.get_lecture(lecture_id)

@router.patch("/edit/{lecture_id}", response_model=LectureRead)
async def edit(
    lecture_id: UUID,
    update_data: LectureUpdate,
    user: User = Depends(authenticate),
    service: LectureService = Depends(get_lecture_service)
):
    return await service.update_lecture(lecture_id, update_data, user)

@router.delete("/delete/{lecture_id}")
async def delete(
    lecture_id: UUID,
    user: User = Depends(authenticate),
    service: LectureService = Depends(get_lecture_service)
):
    await service.delete_lecture(lecture_id, user)
    return Status.success("Deleted successfully")