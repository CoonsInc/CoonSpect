from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserRead(UserBase):
    id: UUID
    
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )

class Token(BaseModel):
    access_token: str
    refresh_token: str

class RefreshToken(BaseModel):
    refresh_token: str
