from fastapi import HTTPException, Request, Depends, Response
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import settings
from src.services.token import Token, TokenType, TokenException
from src.infra.sql.session import get_db
from src.infra.sql.models.user import User
import src.crud.user as user_cruds

COOKIE_PARAMS = {
    "httponly": True,
    "samesite": "lax",
    "secure": False,
    "max_age": 1
}

def create_auth_cookie(uuid: UUID, response: Response):
    access_token = Token.from_type(uuid, TokenType.ACCESS)
    refresh_token = Token.from_type(uuid, TokenType.REFRESH)

    response.set_cookie(
        key="access_token",
        value = access_token.encode(),
        **{**COOKIE_PARAMS, "max_age": settings.JWT_ACCESS_EXPIRE_MINUTES * 60}
    )
    response.set_cookie(
        key="refresh_token",
        value = refresh_token.encode(), 
        **{**COOKIE_PARAMS, "max_age": settings.JWT_REFRESH_EXPIRE_DAYS * 86400}
    )

async def block_auth_cookie(request: Request, response: Response) -> UUID:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token is None:
        raise HTTPException(400, "Expected refresh token")
    
    refresh_token_data = await _decode_token(refresh_token, TokenType.REFRESH)

    if access_token is not None:
        try:
            access_token_data: Token = await _decode_token(access_token, TokenType.ACCESS)

            if access_token_data.uuid != refresh_token_data.uuid:
                raise HTTPException(400, "Different uuid in tokens")
            
            await access_token_data.to_blacklist()
            response.delete_cookie(key="access_token", path="/")
        except TokenException:
            pass
    
    await refresh_token_data.to_blacklist()
    response.delete_cookie(key="refresh_token", path="/")

    return refresh_token_data.uuid

async def authorize(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = await _decode_token(token, TokenType.ACCESS)
    
    user = await user_cruds.get_by_id(db, token_data.uuid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def _decode_token(token_encoded: str, expecting_type: TokenType) -> Token:
    try:
        token = await Token.decode(token_encoded)

        if token.token_type != expecting_type:
            raise HTTPException(status_code=401, detail=f"Expected \"{expecting_type}\" token, found \"{token.token_type}\"")

        return token
    except TokenException as e:
        raise HTTPException(status_code=401, detail=str(e))
