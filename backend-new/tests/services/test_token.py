import pytest
import jwt
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta
from redis.asyncio import Redis

from src.services.token import TokenService, TokenException, TokenExpiredException
from src.models.token import Token, TokenType
from src.settings import settings

@pytest.fixture
def token_service(fake_redis: Redis) -> TokenService:
    return TokenService(fake_redis)

@pytest.mark.asyncio
async def test_create_token_access(token_service: TokenService) -> None:
    user_id: UUID = uuid4()
    token: Token = token_service.create_token(user_id, TokenType.ACCESS)
    
    assert token.uuid == user_id
    assert token.token_type == TokenType.ACCESS
    # Проверяем, что время экспирации установилось примерно верно (+15 мин из настроек)
    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    assert abs((token.expire - expected_exp).total_seconds()) < 5

@pytest.mark.asyncio
async def test_blacklist_flow(token_service: TokenService, fake_redis: Redis) -> None:
    """Проверка добавления в блэклист и последующей валидации."""
    user_id: UUID = uuid4()
    # Создаем токен, который истечет через час
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    token_obj = Token(user_id, exp, TokenType.ACCESS)
    encoded = token_obj.encode()
    
    # 1. Добавляем в блэклист
    await token_service.add_to_blacklist(token_obj)
    
    # Проверяем, что в Redis появился ключ
    exists = await fake_redis.exists(f"token:blacklist:{encoded}")
    assert exists == 1
    
    # 2. Пытаемся декодировать — должно упасть, так как токен отозван
    with pytest.raises(TokenException) as exc:
        await token_service.decode_and_validate(encoded)
    assert "revoked" in str(exc.value)

@pytest.mark.asyncio
async def test_decode_and_validate_success(token_service: TokenService) -> None:
    user_id: UUID = uuid4()
    token_obj = token_service.create_token(user_id, TokenType.ACCESS)
    encoded = token_obj.encode()
    
    decoded: Token = await token_service.decode_and_validate(encoded)
    
    assert decoded.uuid == user_id
    assert decoded.token_type == TokenType.ACCESS
    # Сравниваем timestamp, так как при кодировании в JWT точность до секунды
    assert int(decoded.expire.timestamp()) == int(token_obj.expire.timestamp())

@pytest.mark.asyncio
async def test_decode_expired_token(token_service: TokenService) -> None:
    """Проверка реакции на просроченный токен."""
    user_id: UUID = uuid4()
    # Создаем уже просроченный токен
    past_exp = datetime.now(timezone.utc) - timedelta(minutes=5)
    token_obj = Token(user_id, past_exp, TokenType.ACCESS)
    encoded = token_obj.encode()
    
    with pytest.raises(TokenExpiredException):
        await token_service.decode_and_validate(encoded)

@pytest.mark.asyncio
async def test_decode_invalid_token(token_service: TokenService) -> None:
    """Проверка реакции на кривую строку вместо токена."""
    with pytest.raises(TokenException) as exc:
        await token_service.decode_and_validate("completely.wrong.token")
    assert "Invalid token" in str(exc.value)

@pytest.mark.asyncio
async def test_blacklist_expiration(token_service: TokenService, fake_redis: Redis) -> None:
    """Проверка, что TTL в Redis выставляется корректно."""
    user_id: UUID = uuid4()
    ttl_seconds = 10
    exp = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    token_obj = Token(user_id, exp, TokenType.ACCESS)
    
    await token_service.add_to_blacklist(token_obj)
    
    real_ttl = await fake_redis.ttl(f"token:blacklist:{token_obj.encode()}")
    # TTL должен быть равен или чуть меньше наших 10 секунд
    assert 0 < real_ttl <= ttl_seconds