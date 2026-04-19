import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from fastapi import HTTPException

from src.services.lecture import LectureService
from src.crud.lecture import LectureCRUD
from src.api.schemas.lecture import LectureUpdate, LecturesPage
from src.infra.sql.models.user import User
from src.infra.sql.models.lecture import Lecture

@pytest.fixture
def lecture_service() -> LectureService:
    lecture_crud = AsyncMock(spec=LectureCRUD)
    return LectureService(lecture_crud)

@pytest.mark.asyncio
async def test_get_lectures_page_invalid_limit(lecture_service: LectureService) -> None:
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lectures_page(
            page=1, limit=0, sort_by="created_at", order="desc", user_id=None
        )
    assert exc.value.status_code == 400

from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_get_lectures_page_success(lecture_service: LectureService) -> None:
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    
    lecture = Lecture(
        id=uuid4(),
        user_id=user_id,
        name="Test Lecture",
        lecturer="Dr. Smith",
        audio_url="http://test.com/audio.mp3",
        text="Some text",
        created_at=now,
        updated_at=now
    )
    user = User(id=user_id, username="test_user")
    lecture.user = user

    lecture_service.lecture_crud.get_list.return_value = ([lecture], 1, 1)  # type: ignore

    result: LecturesPage = await lecture_service.get_lectures_page(
        page=1, limit=10, sort_by="name", order="asc", user_id=None
    )
    
    assert result.total == 1
    assert result.items[0].name == "Test Lecture"

@pytest.mark.asyncio
async def test_update_lecture_access_denied(lecture_service: LectureService) -> None:
    owner_id = uuid4()
    stranger_id = uuid4()
    lecture_id = uuid4()
    
    lecture = Lecture(
        id=lecture_id,
        user_id=owner_id,
        name="Old",
        text="text",
        lecturer="prof",
        audio_url="url"
    )
    lecture_service.lecture_crud.read.return_value = lecture # type: ignore
    
    stranger = User(id=stranger_id, username="hacker")
    update_data = LectureUpdate(name="New Name")

    with pytest.raises(HTTPException) as exc:
        await lecture_service.update_lecture(lecture_id, update_data, stranger)
    
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_lecture_success(lecture_service: LectureService) -> None:
    user_id = uuid4()
    lecture_id = uuid4()
    
    lecture = Lecture(id=lecture_id, user_id=user_id, name="x", text="t", lecturer="l", audio_url="a")
    lecture_service.lecture_crud.read.return_value = lecture # type: ignore
    
    user = User(id=user_id, username="owner")
    await lecture_service.delete_lecture(lecture_id, user)
    
    lecture_service.lecture_crud.delete.assert_called_once_with(db_obj=lecture) # type: ignore

@pytest.mark.asyncio
async def test_get_lecture_not_found(lecture_service: LectureService) -> None:
    # Важно: сервис вызывает read_with_user, а не read
    lecture_service.lecture_crud.read_with_user.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lecture(uuid4())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_lectures_page_invalid_sort(lecture_service: LectureService) -> None:
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lectures_page(
            page=1, limit=10, sort_by="illegal_field", order="desc", user_id=None
        )
    assert exc.value.status_code == 400
    assert "Invalid sort field" in exc.value.detail

@pytest.mark.asyncio
async def test_update_lecture_success(lecture_service: LectureService) -> None:
    user_id = uuid4()
    lecture_id = uuid4()
    now = datetime.now(timezone.utc)
    
    original_lecture = Lecture(
        id=lecture_id,
        user_id=user_id,
        name="Old Name",
        text="some text",
        lecturer="Dr. A",
        audio_url="old/url",
        created_at=now,
        updated_at=now
    )
    original_lecture.user = User(id=user_id, username="owner")
    
    updated_lecture = Lecture(
        id=lecture_id,
        user_id=user_id,
        name="Brand New Name",
        text="some text",
        lecturer="Dr. A",
        audio_url="old/url",
        created_at=now,
        updated_at=now
    )
    updated_lecture.user = User(id=user_id, username="owner")
    
    lecture_service.lecture_crud.read.return_value = original_lecture # type: ignore
    lecture_service.lecture_crud.update.return_value = updated_lecture # type: ignore
    
    user = User(id=user_id, username="owner")
    update_data = LectureUpdate(name="Brand New Name")
    
    result = await lecture_service.update_lecture(lecture_id, update_data, user)
    
    lecture_service.lecture_crud.update.assert_called_once() # type: ignore
    assert result.name == "Brand New Name"

@pytest.mark.asyncio
async def test_update_lecture_not_found(lecture_service: LectureService) -> None:
    lecture_service.lecture_crud.read.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.update_lecture(uuid4(), LectureUpdate(name="?"), User(id=uuid4()))
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_lecture_access_denied(lecture_service: LectureService) -> None:
    owner_id = uuid4()
    stranger_id = uuid4()
    lecture_id = uuid4()
    
    lecture = Lecture(id=lecture_id, user_id=owner_id, name="x", text="t", lecturer="l", audio_url="a")
    lecture_service.lecture_crud.read.return_value = lecture # type: ignore
    
    stranger = User(id=stranger_id, username="stranger")
    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_lecture(lecture_id, stranger)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_lecture_not_found(lecture_service: LectureService) -> None:
    lecture_service.lecture_crud.read.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_lecture(uuid4(), User(id=uuid4()))
    assert exc.value.status_code == 404