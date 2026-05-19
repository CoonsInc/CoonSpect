from fastapi import APIRouter, Depends, Request, Response

from src.api.schemas.status import Status
from src.api.schemas.user import UserCreate
from src.services.auth import AuthService, AuthTokens, get_auth_service
from src.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_PARAMS = {"httponly": True, "samesite": "lax", "secure": False}


def set_auth_cookies(response: Response, tokens: AuthTokens) -> None:
    """Хелпер для установки кук в ответ."""
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        max_age=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        **COOKIE_PARAMS,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        max_age=settings.JWT_REFRESH_EXPIRE_DAYS * 86400,
        **COOKIE_PARAMS,
    )


def delete_auth_cookies(response: Response) -> None:
    """Хелпер для удаления кук."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


@router.post("/register", response_model=Status)
async def register(
    content: UserCreate,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.register(content)
    set_auth_cookies(response, tokens)
    return Status.success()


@router.post("/login", response_model=Status)
async def login(
    content: UserCreate,
    response: Response,
    service: AuthService = Depends(dependency=get_auth_service),
):
    tokens = await service.login(content)
    set_auth_cookies(response, tokens)
    return Status.success()


@router.post("/refresh", response_model=Status)
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    old_refresh = request.cookies.get("refresh_token")
    new_tokens = await service.refresh(old_refresh)
    set_auth_cookies(response, new_tokens)
    return Status.success()


@router.post("/logout", response_model=Status)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(
        access_raw=request.cookies.get("access_token"),
        refresh_raw=request.cookies.get("refresh_token"),
    )
    delete_auth_cookies(response)
    return Status.success()
