from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import cast

from src.app.api.schemas.user import UserCreate
from src.app.api.schemas.status import Status
from src.app.infra.sql.session import get_db
from src.app.services.auth import generate_tokens, set_auth_cookies, decode_token
from src.app.services.security import verify_password, TokenType
import src.app.crud.user as user_crud
from src.app.infra.redis import redis

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(content: UserCreate, response: Response, db: Session = Depends(get_db)):
    if user_crud.get_by_username(db, content.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = user_crud.create(db, content.username, content.password)
    
    tokens = generate_tokens(cast(UUID, user.id))
    set_auth_cookies(response, tokens)
    return Status.success()

@router.post("/login")
async def login(content: UserCreate, response: Response, db: Session = Depends(get_db)):
    user = user_crud.get_by_username(db, content.username)
    if not user or not verify_password(content.password, cast(str, user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = generate_tokens(cast(UUID, user.id))
    set_auth_cookies(response, tokens)
    return Status.success()

@router.post("/refresh")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    if await redis.get(f"blacklist:{refresh_token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    token_data = await decode_token(refresh_token, TokenType.REFRESH)
    
    await token_data.to_blacklist()

    tokens = generate_tokens(token_data.uuid)
    set_auth_cookies(response, tokens)
    
    return {"status": "ok"}

@router.post("/logout")
async def logout(request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if access_token:
        try:
            data = await decode_token(access_token, TokenType.ACCESS)
            await data.to_blacklist()
        except:
            pass
    
    if refresh_token:
        try:
            data = await decode_token(refresh_token, TokenType.REFRESH)
            await data.to_blacklist()
        except:
            pass
    
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    return Status.success()
