from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.app.db.redis import redis_sync as redis
from src.app.api.schemas.user import UserCreate
from src.app.api.schemas.token import RefreshToken, RefreshAccessTokens
from src.app.api.schemas.status import Status
from src.app.db.session import get_db
from src.app.api.tools import decode_token, generate_tokens
from src.app.security import Token, hash_password, verify_password

from src.app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RefreshAccessTokens)
async def register(content: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == content.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = User(
        username=content.username,
        password_hash=hash_password(content.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return generate_tokens(user.id)

@router.post("/login", response_model=RefreshAccessTokens)
async def login(content: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == content.username).first()
    if user == None:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    if not verify_password(content.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return generate_tokens(user.id)

@router.post("/refresh", response_model=RefreshAccessTokens)
async def refresh(content: RefreshToken):
    refresh_token = decode_token(content.refresh_token, Token.TokenType.REFRESH)
    
    blacklist_ttl = max((refresh_token.expire - datetime.now(timezone.utc)).seconds, 1)
    
    redis.setex(f"blacklist:{content.refresh_token}", blacklist_ttl, "true")

    return generate_tokens()

@router.post("/logout", response_model=Status)
async def logout(content: RefreshAccessTokens):
    access_token = decode_token(content.access_token, Token.TokenType.ACCESS)
    refresh_token = decode_token(content.refresh_token, Token.TokenType.REFRESH)

    blacklist_access_ttl = max((access_token.expire - datetime.now(timezone.utc)).seconds, 1)
    blacklist_refresh_ttl = max((refresh_token.expire - datetime.now(timezone.utc)).seconds, 1)
    
    redis.setex(f"blacklist:{content.refresh_token}", blacklist_access_ttl, "true")
    redis.setex(f"blacklist:{content.access_token}", blacklist_refresh_ttl, "true")
    
    return Status.success()
