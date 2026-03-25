from fastapi import APIRouter, Depends

from src.api.schemas.user import UserRead
from src.infra.sql.models.user import User
from src.services.auth import authorize

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(authorize)
):
    return current_user
