from fastapi import HTTPException, Request, Depends, Response
from uuid import UUID
from sqlalchemy.orm import Session

from src.app.settings import settings
from src.app.services.security import Token, TokenType
from src.app.infra.sql.session import get_db
from src.app.infra.redis import redis
from src.app.infra.sql.models.user import User
import src.app.crud.user as user_cruds

COOKIE_PARAMS = {
    "httponly": True,
    "samesite": "lax",
    "secure": False,
    "max_age": 1
}

def generate_tokens(uuid: UUID) -> dict[str, str]:
    """Для заданного UUID возвращает 2 токена: access_token и refresh_token"""
    access_token = Token.from_type(uuid, TokenType.ACCESS)
    refresh_token = Token.from_type(uuid, TokenType.REFRESH)
    return {
        "access_token": access_token.encode(),
        "refresh_token": refresh_token.encode()
    }

async def decode_token(token_encoded: str, expecting_type: TokenType) -> Token:
    try:
        token = await Token.decode(token_encoded)

        if token.token_type != expecting_type:
            raise HTTPException(status_code=401, detail=f"Expected \"{expecting_type}\" token, found \"{token.token_type}\"")

        return token
    except Exception as e:
        print(f"Suspitious error in decode_token: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    
def set_auth_cookies(response: Response, tokens: dict[str, str]):
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        **{**COOKIE_PARAMS, "max_age": settings.JWT_ACCESS_EXPIRE_MINUTES * 60}
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"], 
        **{**COOKIE_PARAMS, "max_age": settings.JWT_REFRESH_EXPIRE_DAYS * 86400}
    )

async def authorize(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_data = await decode_token(token, TokenType.ACCESS)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_cruds.get_by_id(db, token_data.uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

