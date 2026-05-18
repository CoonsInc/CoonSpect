from fastapi import APIRouter, Depends

from src.api.schemas.lecture import LecturesPage
from src.api.schemas.user import UserRead
from src.common.sorting import LectureSortBy, SortOrder
from src.infra.db.models.user import User
from src.services.auth import authenticate
from src.services.lecture import LectureService, get_lecture_service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(authenticate)):
    return user


@router.get("/lectures", response_model=LecturesPage)
async def get_lectures_page(
    page: int = 1,
    limit: int = 20,
    sort_by: LectureSortBy = LectureSortBy.CREATED_AT,
    order: SortOrder = SortOrder.DESC,
    search_name: str | None = None,
    lecture_service: LectureService = Depends(get_lecture_service),
    user: User = Depends(authenticate),
):
    return await lecture_service.get_lectures_page(
        page, limit, sort_by, order, user.id, search_name, user.id
    )
