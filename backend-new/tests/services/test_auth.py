import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from uuid import uuid4
from typing import Any

from src.services.auth import create_auth_cookie, authorize, block_auth_cookie
from src.services.token import Token, TokenType

@pytest.mark.asyncio
async def test_create_auth_cookie():
    response = MagicMock(spec=Response)
    user_uuid = uuid4()
    
    create_auth_cookie(user_uuid, response)
    
    assert response.set_cookie.call_count == 2
    calls = response.set_cookie.call_args_list
    keys = [call.kwargs["key"] for call in calls]
    assert "access_token" in keys
    assert "refresh_token" in keys

@pytest.mark.asyncio
async def test_authorize_success(mock_redis: Redis, db_session: AsyncSession):
    """Успешная авторизация по валидному токену."""
    user_uuid = uuid4()
    token = Token.from_type(user_uuid, TokenType.ACCESS).encode()
    
    request = MagicMock(spec=Request)
    request.cookies = {"access_token": token}
    
    mock_user = MagicMock()
    mock_user.uuid = user_uuid
    
    mock_redis.exists.return_value = False # type: ignore
    
    # ПАТЧ: используем AsyncMock для асинхронного CRUD
    with patch("src.crud.user.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
        mock_get_by_id.return_value = mock_user
        
        # Передаем реальную сессию db_session
        user = await authorize(request, db=db_session)
        
        assert user.uuid == user_uuid
        # ПРОВЕРКА: ждем асинхронного вызова
        mock_get_by_id.assert_awaited_once_with(db_session, user_uuid)

@pytest.mark.asyncio
async def test_authorize_no_token_raises_401(db_session):
    """Ошибка 401, если кука access_token отсутствует."""
    request = MagicMock(spec=Request)
    request.cookies = {}
    
    with pytest.raises(HTTPException) as exc:
        await authorize(request, db=db_session)
    
    assert exc.value.status_code == 401
    assert "Not authenticated" in exc.value.detail

@pytest.mark.asyncio
async def test_block_auth_cookie(mock_redis):
    user_uuid = uuid4()
    access = Token.from_type(user_uuid, TokenType.ACCESS).encode()
    refresh = Token.from_type(user_uuid, TokenType.REFRESH).encode()
    
    request = MagicMock(spec=Request)
    request.cookies = {"access_token": access, "refresh_token": refresh}
    response = MagicMock(spec=Response)
    
    mock_redis.exists.return_value = False
    
    returned_uuid = await block_auth_cookie(request, response)
    
    assert returned_uuid == user_uuid
    assert response.delete_cookie.call_count == 2
    assert mock_redis.setex.call_count == 2

@pytest.mark.asyncio
async def test_authorize_invalid_token_type(mock_redis, db_session: AsyncSession):
    user_uuid = uuid4()
    wrong_token = Token.from_type(user_uuid, TokenType.REFRESH).encode()
    
    request = MagicMock(spec=Request)
    request.cookies = {"access_token": wrong_token}
    mock_redis.exists.return_value = False
    
    with pytest.raises(HTTPException) as exc:
        await authorize(request, db=db_session)
    
    assert exc.value.status_code == 401
    assert f"Expected \"{TokenType.ACCESS}\" token" in exc.value.detail
