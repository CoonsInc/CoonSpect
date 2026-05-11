from fastapi import APIRouter, Depends

from src.api.schemas.user import UserRead
from src.infra.db.models.user import User
from src.services.auth import authenticate

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(authenticate)):
    return current_user
