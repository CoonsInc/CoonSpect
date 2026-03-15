from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from src.app.api.schemas.user import UserRead
from src.app.security import Token, TokenType
from src.app.clients.sql.session import get_db
from src.app.clients.sql.models.user import User
from src.app.api.schemas.token import RefreshAccessTokens
from src.app.clients.redis import redis_async as redis

auth_bearer_header = HTTPBearer()

def decode_token(token_encoded: str, expecting_type: TokenType) -> Token:
    try:
        token = Token.decode(token_encoded)

        if token.token_type != expecting_type:
            raise HTTPException(status_code=401, detail=f"Expected \"{expecting_type}\" token, found \"{token.token_type}\"")

        return token
    except Exception as e:
        print(f"Suspitious error in decode_token: {e}")
        raise HTTPException(status_code=401, detail=str(e))

def access_token_request(
    auth_header: HTTPAuthorizationCredentials = Depends(auth_bearer_header),
    db: Session = Depends(get_db)
) -> UserRead:
    token = decode_token(auth_header.credentials, TokenType.ACCESS)
    
    user = db.query(User).filter(User.id == token.uuid).first()
    if user == None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserRead.model_validate(user)

def generate_tokens(uuid: UUID) -> RefreshAccessTokens:
    access_token = Token.from_type(uuid, TokenType.ACCESS)
    refresh_token = Token.from_type(uuid, TokenType.REFRESH)
    return RefreshAccessTokens(access_token=access_token.encode(), refresh_token=refresh_token.encode())

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if await redis.get(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    try:
        token_data = decode_token(token, TokenType.ACCESS)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == token_data.uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
