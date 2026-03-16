from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.app.clients.redis import redis_sync as redis
from src.app.api.schemas.user import UserCreate
from src.app.api.schemas.status import Status
from src.app.clients.sql.session import get_db
from src.app.api.tools import decode_token, generate_tokens
from src.app.security import TokenType, hash_password, verify_password
from src.app.settings import settings

from src.app.clients.sql.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_PARAMS = {
    "httponly": True,
    "samesite": "lax",
    "secure": False,
    "max_age": settings.JWT_ACCESS_EXPIRE_MINUTES,
}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(content: UserCreate, db: Session = Depends(get_db), response: Response = None):
    if db.query(User).filter(User.username == content.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = User(
        username=content.username,
        password_hash=hash_password(content.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    tokens = generate_tokens(user.id)
    
    response.set_cookie(key="access_token", value=tokens.access_token, **COOKIE_PARAMS)
    response.set_cookie(
        key="refresh_token", 
        value=tokens.refresh_token, 
        **{**COOKIE_PARAMS, "max_age": settings.JWT_REFRESH_EXPIRE_DAYS}
    )
    
    return Status.success()

@router.post("/login")
async def login(content: UserCreate, db: Session = Depends(get_db), response: Response = None):
    user = db.query(User).filter(User.username == content.username).first()
    if not user or not verify_password(content.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    tokens = generate_tokens(user.id)
    
    response.set_cookie(key="access_token", value=tokens.access_token, **COOKIE_PARAMS)
    response.set_cookie(
        key="refresh_token", 
        value=tokens.refresh_token, 
        **{**COOKIE_PARAMS, "max_age": settings.JWT_REFRESH_EXPIRE_DAYS}
    )
    
    return Status.success()

@router.post("/refresh")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    if redis.get(f"blacklist:{refresh_token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    token_data = decode_token(refresh_token, TokenType.REFRESH)
    
    ttl = max((token_data.expire - datetime.now(timezone.utc)).seconds, 1)
    redis.setex(f"blacklist:{refresh_token}", ttl, "true")

    tokens = generate_tokens(token_data.sub)
    
    response.set_cookie(key="access_token", value=tokens.access_token, **COOKIE_PARAMS)
    response.set_cookie(
        key="refresh_token", 
        value=tokens.refresh_token, 
        **{**COOKIE_PARAMS, "max_age": settings.JWT_REFRESH_EXPIRE_DAYS}
    )
    
    return {"status": "ok"}

@router.post("/logout")
async def logout(request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if access_token:
        try:
            data = decode_token(access_token, TokenType.ACCESS)
            ttl = max((data.expire - datetime.now(timezone.utc)).seconds, 1)
            redis.setex(f"blacklist:{access_token}", ttl, "true")
        except: pass
    
    if refresh_token:
        try:
            data = decode_token(refresh_token, TokenType.REFRESH)
            ttl = max((data.expire - datetime.now(timezone.utc)).seconds, 1)
            redis.setex(f"blacklist:{refresh_token}", ttl, "true")
        except: pass
    
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    return Status.success()
