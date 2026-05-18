from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.models.lecture import Lecture
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


@pytest.mark.asyncio
async def test_get_my_lectures_success(
    client: AsyncClient, db_session: AsyncSession, sample_user: User, authorize_override
) -> None:
    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="My Public",
                user_id=sample_user.id,
                public=True,
                text=".",
                audio_url=".",
            ),
            Lecture(
                id=uuid4(),
                name="My Private",
                user_id=sample_user.id,
                public=False,
                text=".",
                audio_url=".",
            ),
        ]
    )
    await db_session.commit()

    authorize_override(sample_user)

    response = await client.get("/user/lectures?page=1&limit=10")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    names = [item["name"] for item in data["items"]]
    assert len(names) == 2
    assert "My Public" in names
    assert "My Private" in names
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_my_lectures_unauthorized(client: AsyncClient) -> None:
    """Проверка: неавторизованный пользователь получает 401."""
    response = await client.get("/user/lectures")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_my_lectures_isolation(
    client: AsyncClient, db_session: AsyncSession, sample_user: User, authorize_override
) -> None:
    """Проверка: пользователь не видит ЧУЖИЕ лекции в этом руте, даже публичные."""
    other_user = User(id=uuid4(), username="other", password_hash="hash")
    db_session.add(other_user)

    db_session.add(
        Lecture(
            id=uuid4(),
            name="Other's Lecture",
            user_id=other_user.id,
            public=True,
            text=".",
            audio_url=".",
        )
    )
    db_session.add(
        Lecture(
            id=uuid4(),
            name="My Lecture",
            user_id=sample_user.id,
            public=True,
            text=".",
            audio_url=".",
        )
    )
    await db_session.commit()

    authorize_override(sample_user)

    response = await client.get("/user/lectures")
    data = response.json()

    names = [item["name"] for item in data["items"]]
    assert "My Lecture" in names
    assert "Other's Lecture" not in names
    assert data["total"] == 1
