from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from src.app.api.schemas.user import UserRead

class LectureRead(BaseModel):
    id: UUID
    user: UserRead
    lecturer: str
    name: str
    audio_url: str
    text: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )

class LecturesPage(BaseModel):
    items: list[LectureRead]
    total: int
    page: int
    pages: int

class LectureUpdate(BaseModel):
    name: Optional[str] = None
    lecturer: Optional[str] = None
    text: Optional[str] = None
