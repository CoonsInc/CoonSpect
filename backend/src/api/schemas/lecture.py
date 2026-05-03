from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

from src.api.schemas.user import UserRead

class LectureCreate(BaseModel):
    user_id: UUID
    name: str = "Мой новый конспект"
    lecturer: str = "Неизвестно"
    audio_url: str | None
    text: str = ""

class LectureRead(BaseModel):
    id: UUID
    user: UserRead
    name: str
    lecturer: str
    audio_url: str | None
    text: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes = True,
        extra = "ignore"
    )

class LecturesPage(BaseModel):
    items: list[LectureRead]
    total: int
    page: int
    pages: int

class LectureUpdate(BaseModel):
    name: str | None = None
    lecturer: str | None = None
    text: str | None = None
