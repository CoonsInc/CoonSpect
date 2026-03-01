from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.app.db.redis import redis_sync as redis
from src.app.api.schemas.user import UserCreate, Token, RefreshToken
from src.app.api.schemas.status import Status
from src.app.db.session import get_db
from src.app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from src.app.api.tools import decode_token

from src.app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
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
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=Token)
async def login(content: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == content.username).first()
    if user == None:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    if not verify_password(content.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh(content: RefreshToken):
    payload = decode_token(content.refresh_token, "refresh")
    
    refresh_exp = payload["exp"]
    refresh_ttl = max(int(refresh_exp - datetime.now(timezone.utc).timestamp()), 1)
    redis.setex(f"blacklist:{content.refresh_token}", refresh_ttl, "true")

    access_token = create_access_token(payload["uuid"])
    refresh_token = create_refresh_token(payload["uuid"])
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/logout", response_model=Status)
async def logout(content: Token):
    access_payload = decode_token(content.access_token, "access")
    refresh_payload = decode_token(content.refresh_token, "refresh")

    refresh_exp = refresh_payload["exp"]
    refresh_ttl = max(int(refresh_exp - datetime.now(timezone.utc).timestamp()), 1)

    access_exp = access_payload["exp"]
    access_ttl = max(int(access_exp - datetime.now(timezone.utc).timestamp()), 1)
    
    redis.setex(f"blacklist:{content.refresh_token}", refresh_ttl, "true")
    redis.setex(f"blacklist:{content.access_token}", access_ttl, "true")
    
    return Status.success()
