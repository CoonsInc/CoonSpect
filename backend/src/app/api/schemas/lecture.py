from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class LectureBase(BaseModel):
    audio_url: Optional[str] = None
    text: Optional[str] = None
    segments_url: Optional[str] = None


class LectureCreate(BaseModel):
    user_id: UUID


class LectureRead(LectureBase):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )
