from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.schemas.lecture import LectureRead, LecturesPage, LectureUpdate
from src.api.schemas.status import Status
from src.infra.db.models.user import User
from src.services.auth import authenticate
from src.services.lecture import LectureService, get_lecture_service

router = APIRouter(prefix="/lecture", tags=["lecture"])


@router.get("/list", response_model=LecturesPage)
async def get_list(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    user_id: UUID | None = None,
    service: LectureService = Depends(get_lecture_service),
):
    return await service.get_lectures_page(
        page=page, limit=limit, sort_by=sort_by, order=order, user_id=user_id
    )


@router.get("/{lecture_id}", response_model=LectureRead)
async def get(lecture_id: UUID, service: LectureService = Depends(get_lecture_service)):
    return await service.get_lecture(lecture_id)


@router.patch("/edit/{lecture_id}", response_model=LectureRead)
async def edit(
    lecture_id: UUID,
    update_data: LectureUpdate,
    user: User = Depends(authenticate),
    service: LectureService = Depends(get_lecture_service),
):
    return await service.update_lecture(lecture_id, update_data, user)


@router.delete("/delete/{lecture_id}", response_model=Status)
async def delete(
    lecture_id: UUID,
    user: User = Depends(authenticate),
    service: LectureService = Depends(get_lecture_service),
):
    await service.delete_lecture(lecture_id, user)
    return Status.success("Deleted successfully")


@router.delete("/audiolink/{lecture_id}", response_model=LectureRead)
async def delete_audiolink(
    lecture_id: UUID,
    user: User = Depends(authenticate),
    service: LectureService = Depends(get_lecture_service),
):
    return await service.delete_audiolink(lecture_id, user)


@router.get("/audiolink/{lecture_id}", response_model=Status)
async def audiolink(
    lecture_id: UUID, service: LectureService = Depends(get_lecture_service)
):
    return Status.success(await service.get_audiolink(lecture_id))
