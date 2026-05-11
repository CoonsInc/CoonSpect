import pytest
from fastapi import status
from httpx import AsyncClient

from src.infra.db.models.user import User


@pytest.mark.asyncio
async def test_get_me_success(
    client: AsyncClient, sample_user: User, authorize_override
) -> None:
    """Проверка получения профиля текущего авторизованного пользователя."""

    authorize_override(sample_user)

    response = await client.get("/user/me")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["username"] == sample_user.username
    assert data["id"] == str(sample_user.id)
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient) -> None:
    """Проверка поведения, если пользователь не авторизован."""
    response = await client.get("/user/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["msg"] == "Not authenticated"
