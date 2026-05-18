from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.api.schemas.user import UserRead


class LectureRead(BaseModel):
    id: UUID
    user: UserRead
    name: str
    lecturer: str
    audio_url: str | None
    text: str
    public: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class LecturesPage(BaseModel):
    items: list[LectureRead]
    total: int
    page: int
    pages: int


class LectureUpdate(BaseModel):
    name: str | None = None
    lecturer: str | None = None
    text: str | None = None
    public: bool | None = None
