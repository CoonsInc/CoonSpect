from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.models.lecture import Lecture
from src.infra.db.models.user import User


@pytest.fixture
async def sample_lecture(db_session: AsyncSession, sample_user: User) -> Lecture:
    lecture = Lecture(
        id=uuid4(),
        name="Base Lecture",
        text="Content",
        audio_url="bucket/test.mp3",
        user_id=sample_user.id,
    )
    db_session.add(lecture)
    await db_session.commit()
    await db_session.refresh(lecture)
    return lecture


@pytest.mark.asyncio
async def test_get_lecture_by_id(client: AsyncClient, sample_lecture: Lecture) -> None:
    response = await client.get(f"/lecture/{sample_lecture.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(sample_lecture.id)


@pytest.mark.asyncio
async def test_get_lectures_list_pagination(
    client: AsyncClient, db_session: AsyncSession, sample_user: User
) -> None:
    for i in range(5):
        db_session.add(
            Lecture(id=uuid4(), name=f"L {i}", text="...", user_id=sample_user.id)
        )
    await db_session.commit()

    response = await client.get("/lecture/list?page=1&limit=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5


@pytest.mark.asyncio
async def test_edit_lecture_success(
    client: AsyncClient, sample_user: User, sample_lecture: Lecture, authorize_override
) -> None:
    authorize_override(sample_user)
    response = await client.patch(
        f"/lecture/edit/{sample_lecture.id}", json={"name": "Updated"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_lecture_success(
    client: AsyncClient, sample_user: User, sample_lecture: Lecture, authorize_override
) -> None:
    authorize_override(sample_user)
    response = await client.delete(f"/lecture/delete/{sample_lecture.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_get_audiolink_route_success(
    client: AsyncClient, sample_lecture: Lecture
) -> None:
    """Тест получения ссылки (теперь возвращает Status)."""
    fake_url = "https://fake.url"
    with patch("src.services.s3.S3Service.get_download_url", return_value=fake_url):
        response = await client.get(f"/lecture/audiolink/{sample_lecture.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "success"

        if "details" in data:
            assert data["details"] == fake_url
        elif "message" in data:
            assert data["message"] == fake_url
        else:
            print(f"\nActual response data: {data}")
            assert fake_url in data.values()


@pytest.mark.asyncio
async def test_delete_audiolink_route_success(
    client: AsyncClient, sample_user: User, sample_lecture: Lecture, authorize_override
) -> None:
    """Тест удаления ссылки через API."""
    authorize_override(sample_user)

    with patch("src.services.s3.S3Service.delete", return_value=None):
        response = await client.delete(f"/lecture/audiolink/{sample_lecture.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_lecture.id)
        assert data["audio_url"] is None


@pytest.mark.asyncio
async def test_delete_lecture_forbidden(
    client: AsyncClient, db_session: AsyncSession, authorize_override
) -> None:
    other_user = User(id=uuid4(), username="other", password_hash="hash")
    foreign_lecture = Lecture(
        id=uuid4(), name="Foreign", text="...", user_id=other_user.id
    )
    db_session.add_all([other_user, foreign_lecture])

    me = User(id=uuid4(), username="me", password_hash="hash")
    db_session.add(me)
    await db_session.commit()

    authorize_override(me)
    response = await client.delete(f"/lecture/delete/{foreign_lecture.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
