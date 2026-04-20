import pytest
from httpx import AsyncClient
from fastapi import status

from src.infra.sql.models.user import User

@pytest.mark.asyncio
async def test_get_me_success(
    client: AsyncClient, 
    sample_user: User, 
    authorize_override
) -> None:
    """Проверка получения профиля текущего авторизованного пользователя."""
    
    # Имитируем успешную авторизацию
    authorize_override(sample_user)

    # Выполняем запрос
    response = await client.get("/user/me")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["username"] == sample_user.username
    assert data["id"] == str(sample_user.id)
    assert "password_hash" not in data

@pytest.mark.asyncio
async def test_get_me_unauthorized(
    client: AsyncClient
) -> None:
    """Проверка поведения, если пользователь не авторизован."""
    response = await client.get("/user/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Проверь ключ ("detail" или "msg"), в зависимости от твоего Exception Handler
    assert response.json()["msg"] == "Not authenticated"