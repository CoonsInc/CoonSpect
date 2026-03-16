from fastapi import APIRouter, Depends

from src.app.api.schemas.user import UserRead
from src.app.clients.sql.models.user import User
from src.app.api.tools import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user