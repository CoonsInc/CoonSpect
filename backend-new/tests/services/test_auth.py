import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.services.auth import AuthService, AuthTokens
from src.services.token import TokenService
from src.services.password import PasswordService
from src.crud.user import UserCRUD
from src.api.schemas.user import UserCreate
from src.infra.sql.models.user import User
from src.models.token import Token, TokenType

@pytest.fixture
def auth_service(db_session: AsyncSession) -> AuthService:
    """Фабрика сервиса с моками для внешних зависимостей."""
    user_crud = UserCRUD(db_session)
    token_service = AsyncMock(spec=TokenService)
    password_service = MagicMock(spec=PasswordService)
    
    return AuthService(
        user_crud=user_crud, 
        token_service=token_service, 
        password_service=password_service
    )

@pytest.mark.asyncio
async def test_register_flow(
    auth_service: AuthService, 
) -> None:
    auth_service.password_service.hash_password.return_value = "hashed_pw" # type: ignore
    
    user_in = UserCreate(username="new_user", password="plain_password")

    mock_token_obj = MagicMock()
    mock_token_obj.encode.return_value = "encoded_jwt"
    auth_service.token_service.create_token.return_value = mock_token_obj # type: ignore

    result: AuthTokens = await auth_service.register(user_in)
    
    assert result.access_token == "encoded_jwt"
    assert result.refresh_token == "encoded_jwt"
    auth_service.password_service.hash_password.assert_called_once_with("plain_password") # type: ignore

@pytest.mark.asyncio
async def test_login_success(
    auth_service: AuthService, 
    db_session: AsyncSession
) -> None:
    user_id: UUID = uuid4()
    user = User(id=user_id, username="login_user", password_hash="hashed_abc")
    db_session.add(user)
    await db_session.commit()
    
    auth_service.password_service.verify_password.return_value = True # type: ignore
    
    # Мокаем объект токена, который возвращает create_token
    mock_token_obj = MagicMock()
    mock_token_obj.encode.return_value = "encoded_jwt"
    auth_service.token_service.create_token.return_value = mock_token_obj # type: ignore
    
    login_data = UserCreate(username="login_user", password="correct_password")
    result: AuthTokens = await auth_service.login(login_data)
    
    assert result.user_id == user_id
    assert result.access_token == "encoded_jwt"
    auth_service.password_service.verify_password.assert_called_once() # type: ignore

@pytest.mark.asyncio
async def test_authorize_success(
    auth_service: AuthService, 
    db_session: AsyncSession
) -> None:
    user_id: UUID = uuid4()
    user = User(id=user_id, username="auth_me", password_hash="...")
    db_session.add(user)
    await db_session.commit()
    
    # Теперь expire — это честный datetime в будущем
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    mock_token_data = Token(user_id, exp_time, TokenType.ACCESS)
    
    auth_service.token_service.decode_and_validate.return_value = mock_token_data # type: ignore
    
    authorized_user: User = await auth_service.authenticate("some_token")
    
    assert authorized_user.id == user_id
    assert authorized_user.username == "auth_me"

@pytest.mark.asyncio
async def test_logout_logic(
    auth_service: AuthService,
) -> None:
    user_id: UUID = uuid4()
    now = datetime.now(timezone.utc)
    
    # Инициализируем токены с datetime
    refresh_data = Token(user_id, now + timedelta(days=7), TokenType.REFRESH)
    access_data = Token(user_id, now + timedelta(minutes=15), TokenType.ACCESS)
    
    auth_service.token_service.decode_and_validate.side_effect = [ # type: ignore
        refresh_data, 
        access_data
    ]
    
    await auth_service.logout(access_raw="access", refresh_raw="refresh")
    
    assert auth_service.token_service.add_to_blacklist.call_count == 2 # type: ignore