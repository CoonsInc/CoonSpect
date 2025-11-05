from pydantic import BaseModel, Field
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    profile: str | None = None
    settings: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserRead(UserBase):
    id: UUID

    class Config:
        orm_mode = True
