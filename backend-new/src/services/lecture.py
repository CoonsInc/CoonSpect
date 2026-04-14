from uuid import UUID
from fastapi import HTTPException
from src.crud.lecture import LectureCRUD
from src.api.schemas.lecture import LectureUpdate, LecturesPage, LectureRead
from src.infra.sql.models.user import User
from typing import cast

class LectureService:
    def __init__(self, lecture_crud: LectureCRUD):
        self.lecture_crud = lecture_crud

    async def get_lectures_page(
        self, 
        page: int, 
        limit: int, 
        sort_by: str, 
        order: str, 
        user_id: UUID | None
    ) -> LecturesPage:
        if limit < 1:
            raise HTTPException(400, "Too low limit value")
        
        allowed_fields = {"name", "created_at", "updated_at"}
        if sort_by not in allowed_fields:
            raise HTTPException(400, "Invalid sort field")
        
        items, total, pages = await self.lecture_crud.get_list(
            page=page, limit=limit, sort_by=sort_by, order=order, user_id=user_id
        )

        return LecturesPage(
            items=cast(list[LectureRead], items),
            total=total,
            page=page,
            pages=pages
        )

    async def get_lecture(self, lecture_id: UUID) -> LectureRead:
        lecture = await self.lecture_crud.read_with_user(lecture_id)
        if lecture is None:
            raise HTTPException(404, "Lecture not found")
        return LectureRead.model_validate(lecture)

    async def update_lecture(
        self, 
        lecture_id: UUID, 
        update_data: LectureUpdate, 
        user: User
    ) -> LectureRead:
        lecture = await self.lecture_crud.read(lecture_id)
        if lecture is None:
            raise HTTPException(404, "Lecture not found")
        
        if cast(UUID, user.id) != cast(UUID, lecture.user_id):
            raise HTTPException(403, "Access denied: You are not the owner")
        
        updated = await self.lecture_crud.update(db_obj=lecture, update_data=update_data)
        return LectureRead.model_validate(updated)

    async def delete_lecture(self, lecture_id: UUID, user: User) -> None:
        lecture = await self.lecture_crud.read(lecture_id)
        if lecture is None:
            raise HTTPException(404, "Lecture not found")
        
        if cast(UUID, user.id) != cast(UUID, lecture.user_id):
            raise HTTPException(403, "Access denied: You are not the owner")
        
        await self.lecture_crud.delete(db_obj=lecture)

from fastapi import Depends
from src.crud.lecture import get_lecture_crud

async def get_lecture_service(
    lecture_crud: LectureCRUD = Depends(get_lecture_crud)
) -> LectureService:
    return LectureService(lecture_crud)
