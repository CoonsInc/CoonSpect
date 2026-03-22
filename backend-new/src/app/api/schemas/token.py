from pydantic import BaseModel

class RefreshToken(BaseModel):
    refresh_token: str

class RefreshAccessTokens(RefreshToken):
    access_token: str

