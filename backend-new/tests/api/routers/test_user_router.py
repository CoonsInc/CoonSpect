import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_me(auth_client: AsyncClient, mock_redis_global):
    # Теперь mock_redis_global автоматически подставил FakeRedis в src.infra.redis
    # Можем даже что-то туда записать вручную для теста:
    # await mock_redis_global.set("some_key", "value")
    
    response = await auth_client.get("/user/me")
    
    assert response.status_code == 200
    assert "integration_user" in response.json()["username"]

@pytest.mark.asyncio
async def test_get_me_with_expired_token(client: AsyncClient, mock_redis_global):
    """Проверка, что с «левой» кукой доступ запрещен."""
    client.cookies.set("access_token", "invalid_garbage_token")
    
    response = await client.get("/user/me")
    
    # Тут сработает твоя реальная проверка и выкинет 401
    assert response.status_code == 401