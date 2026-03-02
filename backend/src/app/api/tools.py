from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from src.app.api.schemas.user import UserRead
from src.app.security import Token
from src.app.db.session import get_db
from src.app.db.models.user import User
from src.app.api.schemas.token import RefreshAccessTokens

auth_bearer_header = HTTPBearer()

def decode_token(token_encoded: str, expecting_type: Token.TokenType) -> Token:
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
    token = decode_token(auth_header.credentials, Token.TokenType.ACCESS)
    
    user = db.query(User).filter(User.id == token.uuid).first()
    if user == None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserRead.model_validate(user)

def generate_tokens(uuid: UUID) -> RefreshAccessTokens:
    access_token = Token.from_type(uuid, Token.TokenType.ACCESS)
    refresh_token = Token.from_type(uuid, Token.TokenType.REFRESH)
    return RefreshAccessTokens(access_token=access_token.encode(), refresh_token=refresh_token.encode())
