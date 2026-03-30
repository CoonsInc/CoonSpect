from uuid import UUID
from typing import NamedTuple
from fastapi import HTTPException, Depends, Request

from src.models.token import Token, TokenType
from src.services.token import TokenService, TokenException, TokenExpiredException, get_token_service
from src.infra.sql.session import get_db
from src.infra.sql.models.user import User
from src.api.schemas.user import UserCreate
from src.services.password import PasswordService, get_password_service
from src.crud.user import UserCRUD, get_user_crud

class AuthTokens(NamedTuple):
    access_token: str
    refresh_token: str
    user_id: UUID

class AuthService:
    def __init__(self, user_crud: UserCRUD, token_service: TokenService, password_service: PasswordService):
        self.user_crud = user_crud
        self.token_service = token_service
        self.password_service = password_service

    async def register(self, content: UserCreate) -> AuthTokens:
        hashed_password = self.password_service.hash_password(content.password)
        
        new_user = User(
            username = content.username,
            password_hash = hashed_password
        )

        await self.user_crud.create(new_user)

        return await self._issue_tokens(new_user.id)

    async def login(self, content: UserCreate) -> AuthTokens:
        user = await self.user_crud.read_by_username(content.username)
        if user is None or not self.password_service.verify_password(content.password, user.password_hash):
            raise HTTPException(401, "Invalid credentials")
        
        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_raw: str | None) -> AuthTokens:
        if refresh_raw is None:
            raise HTTPException(400, "Refresh token required")
            
        token_data = await self._validate_token_type(refresh_raw, TokenType.REFRESH)
        await self.token_service.add_to_blacklist(token_data)
        
        return await self._issue_tokens(token_data.uuid)

    async def logout(self, access_raw: str | None, refresh_raw: str | None):
        if refresh_raw is None:
            raise HTTPException(400, "Expected refresh token")

        refresh_token = await self._validate_token_type(refresh_raw, TokenType.REFRESH)
        
        if access_raw is not None:
            try:
                access_token = await self._validate_token_type(access_raw, TokenType.ACCESS)
                if access_token.uuid == refresh_token.uuid:
                    await self.token_service.add_to_blacklist(access_token)
            except (TokenException, HTTPException):
                pass

        await self.token_service.add_to_blacklist(refresh_token)

    async def authorize(self, access_raw: str | None) -> User:
        if access_raw is None:
            raise HTTPException(401, "Not authenticated")

        try:
            token_data = await self._validate_token_type(access_raw, TokenType.ACCESS)
            user = await self.user_crud.read(token_data.uuid)
            if user is None:
                raise HTTPException(404, "User not found")
            return user
        except TokenExpiredException:
            raise HTTPException(401, "Token expired")
        except TokenException as e:
            raise HTTPException(401, str(e))
        
    async def _issue_tokens(self, user_id: UUID) -> AuthTokens:
        """Внутренний метод для генерации пары токенов."""
        access = self.token_service.create_token(user_id, TokenType.ACCESS)
        refresh = self.token_service.create_token(user_id, TokenType.REFRESH)
        return AuthTokens(
            access_token=access.encode(),
            refresh_token=refresh.encode(),
            user_id=user_id
        )

    async def _validate_token_type(self, encoded_token: str, expected_type: TokenType) -> Token:
        token = await self.token_service.decode_and_validate(encoded_token)
        if token.token_type != expected_type:
            raise HTTPException(401, f"Expected {expected_type}, found {token.token_type}")
        return token

def get_auth_service(
    user_crud: UserCRUD = Depends(get_user_crud), 
    token_service: TokenService = Depends(get_token_service),
    password_service: PasswordService = Depends(get_password_service)
) -> AuthService:
    return AuthService(user_crud, token_service, password_service)

async def authorize(
    request: Request, 
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.authorize(request.cookies.get("access_token"))



# TODO: Разобраться с этим говном

from http.cookies import SimpleCookie
from fastapi import WebSocket, status, Depends
# Твои внутренние импорты (поправь пути, если они другие)
from src.services.auth import decode_token, TokenType 
from src.infra.redis import get_redis # Твой инстанс редиса

#
async def authorize_websocket(websocket: WebSocket) -> str:
    """Проверяет куки, токен и наличие задачи в Redis для WebSocket."""
    
    cookie_header = websocket.headers.get("cookie")
    if not cookie_header:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No cookies")
        raise Exception("WebSocket Auth Failed: No cookies")
    
    cookies = SimpleCookie(cookie_header)
    access_token_value = cookies.get("access_token")
    
    if not access_token_value:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No access token")
        raise Exception("WebSocket Auth Failed: No access token")
        
    try:
        # 1. Декодируем токен
        token_data = decode_token(access_token_value.value, TokenType.ACCESS)
        
        # 2. Проверка блэклиста в Redis
        if await redis_async.get(f"blacklist:{access_token_value.value}"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token revoked")
            raise Exception("WebSocket Auth Failed: Token revoked")
            
        task_id = str(token_data.uuid)
        
        # 3. Проверяем существование задачи
        if not await redis_async.exists(f"task:{task_id}"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Task not found")
            raise Exception("WebSocket Auth Failed: Task not found")
            
        return task_id
        
    except Exception as e:
        # Если при декодировании токена упала ошибка
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        raise e