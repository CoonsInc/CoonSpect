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
        audio_url="lectures/test.mp3",
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
            Lecture(
                id=uuid4(),
                name=f"L {i}",
                text="...",
                user_id=sample_user.id,
                audio_url="lectures/test.mp3",
                public=True,
            )
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
    client: AsyncClient,
    sample_lecture: Lecture,
    sample_user: User,
    authorize_override
) -> None:
    """Тест получения ссылки (теперь возвращает Status)."""
    authorize_override(sample_user)

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
async def test_get_audiolink_route_no_auth_fail(
    client: AsyncClient,
    sample_lecture: Lecture
) -> None:
    """Тест получения ссылки (теперь возвращает Status)."""
    fake_url = "https://fake.url"
    with patch("src.services.s3.S3Service.get_download_url", return_value=fake_url):
        response = await client.get(f"/lecture/audiolink/{sample_lecture.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_audiolink_route_public_no_auth_success(
    client: AsyncClient,
    sample_lecture: Lecture
) -> None:
    """Тест получения ссылки (теперь возвращает Status)."""
    sample_lecture.public = True
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
        id=uuid4(),
        name="Foreign",
        text="...",
        user_id=other_user.id,
        audio_url="lectures/test.mp3",
    )
    db_session.add_all([other_user, foreign_lecture])

    me = User(id=uuid4(), username="me", password_hash="hash")
    db_session.add(me)
    await db_session.commit()

    authorize_override(me)
    response = await client.delete(f"/lecture/delete/{foreign_lecture.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_lectures_list_search(
    client: AsyncClient, db_session: AsyncSession, sample_user: User
) -> None:
    """Проверка поиска по названию лекции."""
    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="Calculus 101",
                user_id=sample_user.id,
                text=".",
                audio_url=".",
                public=True,
            ),
            Lecture(
                id=uuid4(),
                name="History of Art",
                user_id=sample_user.id,
                text=".",
                audio_url=".",
                public=True,
            ),
            Lecture(
                id=uuid4(),
                name="Advanced Calculus",
                user_id=sample_user.id,
                text=".",
                audio_url=".",
                public=True,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get("/lecture/list?search_name=calculus")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 2
    for item in data["items"]:
        assert "Calculus" in item["name"]


@pytest.mark.asyncio
async def test_get_lectures_list_privacy_filter(
    client: AsyncClient, db_session: AsyncSession, sample_user: User
) -> None:
    """Проверка приватности: аноним видит только public, владелец видит всё."""
    user_a_id = sample_user.id

    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="Public A",
                user_id=user_a_id,
                public=True,
                text=".",
                audio_url=".",
            ),
            Lecture(
                id=uuid4(),
                name="Private A",
                user_id=user_a_id,
                public=False,
                text=".",
                audio_url=".",
            ),
        ]
    )
    await db_session.commit()

    response = await client.get("/lecture/list")
    assert response.status_code == 200
    data = response.json()
    names = [item["name"] for item in data["items"]]
    assert "Public A" in names
    assert "Private A" not in names

    response = await client.get(f"/lecture/list?user_id={user_a_id}")
    data = response.json()
    names = [item["name"] for item in data["items"]]
    assert "Public A" in names
    assert "Private A" not in names


@pytest.mark.asyncio
async def test_get_lectures_list_privacy_filter_anonymous(
    client: AsyncClient, db_session: AsyncSession, sample_user: User
) -> None:
    owner_id = sample_user.id

    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="Public Lecture",
                user_id=owner_id,
                public=True,
                text=".",
                audio_url=".",
            ),
            Lecture(
                id=uuid4(),
                name="Private Lecture",
                user_id=owner_id,
                public=False,
                text=".",
                audio_url=".",
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(f"/lecture/list?user_id={owner_id}")

    assert response.status_code == 200
    data = response.json()

    names = [item["name"] for item in data["items"]]

    assert "Public Lecture" in names
    assert "Private Lecture" not in names
    assert data["total"] == 1
