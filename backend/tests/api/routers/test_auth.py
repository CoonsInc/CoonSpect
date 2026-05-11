import pytest
from fastapi import status
from httpx import AsyncClient

from src.api.schemas.user import UserCreate
from src.infra.db.models.user import User


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    payload = UserCreate(username="new_user_unique", password="strong_password")
    response = await client.post("/auth/register", json=payload.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_user: User) -> None:
    payload = {"username": sample_user.username, "password": "password"}
    response = await client.post("/auth/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_logout_clears_cookies(client: AsyncClient, sample_user: User) -> None:
    await client.post(
        "/auth/login", json={"username": sample_user.username, "password": "password"}
    )

    response = await client.post("/auth/logout")

    assert response.status_code == status.HTTP_200_OK
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "Max-Age=0" in set_cookie_header or "expires=" in set_cookie_header.lower()


@pytest.mark.asyncio
async def test_refresh_token_flow(client: AsyncClient, sample_user: User) -> None:
    await client.post(
        "/auth/login", json={"username": sample_user.username, "password": "password"}
    )

    # Обновляемся
    response = await client.post("/auth/refresh")

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.headers.get("set-cookie", "")
