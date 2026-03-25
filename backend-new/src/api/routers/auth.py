from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import cast

from src.api.schemas.user import UserCreate
from src.api.schemas.status import Status
from src.infra.sql.session import get_db
from src.services.auth import create_auth_cookie, block_auth_cookie
from src.services.password import verify_password
import src.crud.user as user_crud
from src.infra.redis import redis

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    content: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    if user_crud.get_by_username(db, content.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = await user_crud.create(db, content.username, content.password)
    
    create_auth_cookie(cast(UUID, user.id), response)

    return Status.success()

@router.post("/login")
async def login(
    content: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_by_username(db, content.username)
    if user is None or not verify_password(content.password, cast(str, user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    create_auth_cookie(cast(UUID, user.id), response)
    return Status.success()

@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    if await redis.get(f"blacklist:{refresh_token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    user_id = await block_auth_cookie(request, response)
    create_auth_cookie(cast(UUID, user_id), response)
    
    return Status.success()

@router.post("/logout")
async def logout(
    request: Request,
    response: Response
):
    await block_auth_cookie(request, response)
    return Status.success()
