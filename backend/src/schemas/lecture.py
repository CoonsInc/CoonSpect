from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class LectureBase(BaseModel):
    audio_url: str | None = None
    text_url: str | None = None
    status: str | None = None
    task_id: str | None = None


class LectureCreate(BaseModel):
    user_id: UUID
    file_path: str | None = None
    s3_url: str | None = None


class LectureRead(LectureBase):
    id: UUID
    user_id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class LectureStatus(BaseModel):
    lecture_id: UUID
    status: str
    task_id: str | None = None
