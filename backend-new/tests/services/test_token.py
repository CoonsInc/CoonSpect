import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from src.services.token import Token, TokenType, TokenException, TokenExpiredException

@pytest.mark.asyncio
async def test_token_encode_decode(mock_settings, mock_redis):
    user_id = uuid4()
    token_obj = Token.from_type(user_id, TokenType.ACCESS)
    
    # Эмулируем отсутствие в блэклисте
    mock_redis.exists.return_value = False
    
    encoded = token_obj.encode()
    decoded_obj = await Token.decode(encoded)
    
    assert decoded_obj.uuid == user_id
    assert decoded_obj.token_type == TokenType.ACCESS

@pytest.mark.asyncio
async def test_token_expired_raises_exception(mock_settings, mock_redis):
    # Явно указываем, что токена НЕТ в блэклисте
    mock_redis.exists.return_value = False
    
    # Создаем токен, который уже протух
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    token_obj = Token(uuid4(), past_time, TokenType.ACCESS)

    encoded = token_obj.encode()

    # Теперь выполнение пройдет проверку блэклиста и упадет на jwt.decode
    with pytest.raises(TokenExpiredException, match="Token expired"):
        await Token.decode(encoded)

@pytest.mark.asyncio
async def test_token_in_blacklist_raises_exception(mock_settings, mock_redis):
    token_obj = Token.from_type(uuid4(), TokenType.ACCESS)
    encoded = token_obj.encode()
    
    # Имитируем, что токен в блэклисте
    mock_redis.exists.return_value = True
    
    with pytest.raises(TokenException, match="Token has been revoked"):
        await Token.decode(encoded)

@pytest.mark.asyncio
async def test_add_to_blacklist(mock_settings, mock_redis):
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    token_obj = Token(uuid4(), expire, TokenType.ACCESS)
    
    await token_obj.to_blacklist()
    
    # Проверяем, что вызывался setex (установка значения с TTL)
    mock_redis.setex.assert_called_once()
    args, _ = mock_redis.setex.call_args
    assert args[0].startswith("token:blacklist:")
    assert isinstance(args[1], int) # TTL

def test_from_type_factory(mock_settings):
    user_id = uuid4()
    token = Token.from_type(user_id, TokenType.REFRESH)
    
    assert token.token_type == TokenType.REFRESH
    assert token.uuid == user_id
    # Проверка, что дата экспирации установилась в будущем
    assert token.expire > datetime.now(timezone.utc)
