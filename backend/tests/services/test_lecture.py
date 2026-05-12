from datetime import UTC, datetime
from unittest.mock import ANY, AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.lecture import LectureRead, LecturesPage
from src.common.sorting import LectureSortBy, SortOrder
from src.crud.lecture import LectureCRUD
from src.infra.db.models.lecture import Lecture
from src.infra.db.models.user import User
from src.services.lecture import LectureService
from src.services.s3 import S3Service


@pytest.fixture
def mock_lecture_crud() -> AsyncMock:
    return AsyncMock(spec=LectureCRUD)


@pytest.fixture
def mock_s3_service() -> AsyncMock:
    return AsyncMock(spec=S3Service)


@pytest.fixture
def lecture_service(mock_lecture_crud, mock_s3_service) -> LectureService:
    return LectureService(lecture_crud=mock_lecture_crud, s3_service=mock_s3_service)


@pytest.fixture
def sample_user():
    return User(id=uuid4(), username="test_user")


@pytest.fixture
def sample_lecture(sample_user):
    """Создает объект лекции для тестов сервиса"""
    now = datetime.now(UTC)
    lecture = Lecture(
        id=uuid4(),
        user_id=sample_user.id,
        name="Test Lecture",
        lecturer="Dr. Smith",
        audio_url="my-bucket/audio.mp3",
        text="Some text",
        created_at=now,
        updated_at=now,
        public=True,  # ← FIX 1: Pydantic требует bool, а не None
    )
    lecture.user = sample_user
    return lecture


@pytest.mark.asyncio
async def test_get_lectures_page_success(
    lecture_service, mock_lecture_crud, sample_lecture
):
    mock_lecture_crud.get_list.return_value = ([sample_lecture], 1, 1)

    result = await lecture_service.get_lectures_page(
        page=1, limit=10, sort_by="name", order="asc", user_id=None
    )

    assert isinstance(result, LecturesPage)
    assert result.total == 1
    assert result.items[0].name == "Test Lecture"


@pytest.mark.asyncio
async def test_get_lecture_success(lecture_service, mock_lecture_crud, sample_lecture):
    mock_lecture_crud.read_with_user.return_value = sample_lecture
    res = await lecture_service.get_lecture(sample_lecture.id)
    assert isinstance(res, LectureRead)
    assert res.id == sample_lecture.id


@pytest.mark.asyncio
async def test_service_delete_audiolink_success(
    lecture_service, mock_lecture_crud, mock_s3_service, sample_lecture, sample_user
):
    sample_lecture.audio_url = "my-bucket/audio.mp3"
    mock_lecture_crud.read.return_value = sample_lecture

    async def side_effect_update(db_obj, update_data):
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        return db_obj

    mock_lecture_crud.update.side_effect = side_effect_update

    res = await lecture_service.delete_audiolink(sample_lecture.id, sample_user)

    assert isinstance(res, LectureRead)
    assert res.audio_url is None
    mock_s3_service.delete.assert_called_once_with("my-bucket", "audio.mp3")


@pytest.mark.asyncio
async def test_service_get_audiolink_success(
    lecture_service, mock_lecture_crud, mock_s3_service, sample_lecture
):
    mock_lecture_crud.read_with_user.return_value = sample_lecture
    mock_s3_service.get_download_url.return_value = "https://presigned-url.com"

    url = await lecture_service.get_audiolink(sample_lecture.id)

    assert isinstance(url, str)
    assert url == "https://presigned-url.com"
    mock_s3_service.get_download_url.assert_called_once_with(
        "my-bucket", "audio.mp3", ANY
    )


@pytest.mark.asyncio
async def test_service_get_audiolink_no_audio(
    lecture_service, mock_lecture_crud, sample_lecture
):
    sample_lecture.audio_url = None
    mock_lecture_crud.read_with_user.return_value = sample_lecture

    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_audiolink(sample_lecture.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_service_delete_lecture_with_audio_success(
    lecture_service, mock_lecture_crud, mock_s3_service, sample_lecture, sample_user
):
    """Проверяем, что при удалении лекции удаляется и запись в БД, и файл в S3."""
    sample_lecture.audio_url = "my-bucket/audio.mp3"
    mock_lecture_crud.read.return_value = sample_lecture

    await lecture_service.delete_lecture(sample_lecture.id, sample_user)

    mock_lecture_crud.delete.assert_called_once_with(db_obj=sample_lecture)

    mock_s3_service.delete.assert_called_once_with("my-bucket", "audio.mp3")


@pytest.mark.asyncio
async def test_service_delete_lecture_no_audio_success(
    lecture_service, mock_lecture_crud, mock_s3_service, sample_lecture, sample_user
):
    """Проверяем, что если у лекции нет аудио, мы просто удаляем запись из БД."""
    sample_lecture.audio_url = None
    mock_lecture_crud.read.return_value = sample_lecture

    await lecture_service.delete_lecture(sample_lecture.id, sample_user)

    mock_lecture_crud.delete.assert_called_once_with(db_obj=sample_lecture)

    mock_s3_service.delete.assert_not_called()


@pytest.mark.asyncio
async def test_service_delete_lecture_access_denied(
    lecture_service, mock_lecture_crud, sample_lecture
):
    """Проверяем, что чужой пользователь не может удалить лекцию."""
    mock_lecture_crud.read.return_value = sample_lecture
    another_user = User(id=uuid4(), username="hacker")

    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_lecture(sample_lecture.id, another_user)

    assert exc.value.status_code == 403
    mock_lecture_crud.delete.assert_not_called()


@pytest.mark.asyncio
async def test_get_lectures_page_invalid_limit(lecture_service):
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lectures_page(
            page=1,
            limit=0,
            sort_by=LectureSortBy.NAME,
            order=SortOrder.ASC,
            user_id=None,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_lectures_page_forwards_params(lecture_service, mock_lecture_crud):
    mock_lecture_crud.get_list.return_value = ([], 0, 1)

    await lecture_service.get_lectures_page(
        page=2,
        limit=15,
        sort_by=LectureSortBy.NAME,
        order=SortOrder.DESC,
        user_id=uuid4(),
        search_name="test",
    )
    mock_lecture_crud.get_list.assert_called_once_with(
        page=2,
        limit=15,
        sort_by=LectureSortBy.NAME,
        order=SortOrder.DESC,
        user_id=ANY,
        search_name="test",
        requester_user_id=None,
    )


@pytest.mark.asyncio
async def test_get_lectures_page_forwards_all_params(
    lecture_service, mock_lecture_crud
):
    """
    Проверяем, что сервис корректно передает все параметры,
    включая search_name и user_id_requester, в CRUD слой.
    """
    mock_lecture_crud.get_list.return_value = ([], 0, 1)
    target_user_id = uuid4()
    requester_id = uuid4()
    search_query = "quantum physics"

    await lecture_service.get_lectures_page(
        page=1,
        limit=20,
        sort_by=LectureSortBy.CREATED_AT,
        order=SortOrder.DESC,
        user_id=target_user_id,
        search_name=search_query,
        requester_user_id=requester_id,
    )

    # Проверяем, что вызов CRUD произошел с правильными аргументами
    mock_lecture_crud.get_list.assert_called_once_with(
        page=1,
        limit=20,
        sort_by=LectureSortBy.CREATED_AT,
        order=SortOrder.DESC,
        user_id=target_user_id,
        search_name=search_query,
        requester_user_id=requester_id,  # Тот самый новый параметр
    )


@pytest.mark.asyncio
async def test_update_lecture_owner_success(
    lecture_service, mock_lecture_crud, sample_lecture, sample_user
):
    """Проверка успешного обновления лекции владельцем."""
    mock_lecture_crud.read.return_value = sample_lecture
    update_data = AsyncMock()  # Или объект LectureUpdate

    mock_lecture_crud.update.return_value = sample_lecture

    await lecture_service.update_lecture(sample_lecture.id, update_data, sample_user)

    mock_lecture_crud.update.assert_called_once_with(
        db_obj=sample_lecture, update_data=update_data
    )


@pytest.mark.asyncio
async def test_update_lecture_access_denied(
    lecture_service, mock_lecture_crud, sample_lecture
):
    """Проверка ошибки 403 при попытке обновить чужую лекцию."""
    mock_lecture_crud.read.return_value = sample_lecture
    stranger = User(id=uuid4(), username="stranger")
    update_data = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await lecture_service.update_lecture(sample_lecture.id, update_data, stranger)

    assert exc.value.status_code == 403
    assert "not the owner" in exc.value.detail
    mock_lecture_crud.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_audiolink_access_denied(
    lecture_service, mock_lecture_crud, sample_lecture
):
    """Проверка ошибки 403 при удалении аудио чужой лекции."""
    mock_lecture_crud.read.return_value = sample_lecture
    stranger = User(id=uuid4(), username="stranger")

    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_audiolink(sample_lecture.id, stranger)

    assert exc.value.status_code == 403
    mock_lecture_crud.update.assert_not_called()
