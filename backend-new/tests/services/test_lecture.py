import pytest
from unittest.mock import AsyncMock, MagicMock  # Добавили MagicMock
from uuid import uuid4, UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.lecture import LectureService
from src.crud.lecture import LectureCRUD
from src.api.schemas.lecture import LectureUpdate, LecturesPage, LectureRead
from src.infra.sql.models.user import User
from src.infra.sql.models.lecture import Lecture

@pytest.fixture
def lecture_service() -> LectureService:
    # Инициализируем с моком CRUD
    lecture_crud = AsyncMock(spec=LectureCRUD)
    return LectureService(lecture_crud)

@pytest.mark.asyncio
async def test_get_lectures_page_invalid_limit(lecture_service: LectureService) -> None:
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lectures_page(
            page=1, limit=0, sort_by="created_at", order="desc", user_id=None
        )
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_get_lectures_page_success(lecture_service: LectureService) -> None:
    user_id = uuid4()
    
    # Создаем "фейковые" данные, которые похожи на объекты из БД
    # Это проще, чем настраивать каждый атрибут у AsyncMock
    mock_lecture = MagicMock(spec=Lecture)
    mock_lecture.id = uuid4()
    mock_lecture.name = "Test Lecture"
    mock_lecture.user_id = user_id
    mock_lecture.lecturer = "Dr. Smith"
    mock_lecture.audio_url = "http://test.com/audio.mp3"
    mock_lecture.text = "Some text"
    
    # Имитируем связь с юзером для схемы LectureRead
    mock_lecture.user = MagicMock(spec=User)
    mock_lecture.user.id = user_id
    mock_lecture.user.username = "test_user"

    lecture_service.lecture_crud.get_list.return_value = ([mock_lecture], 1, 1) # type: ignore
    
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
    
    mock_lecture = MagicMock(spec=Lecture)
    mock_lecture.id = lecture_id
    mock_lecture.user_id = owner_id
    lecture_service.lecture_crud.read.return_value = mock_lecture # type: ignore
    
    stranger = User(id=stranger_id, username="hacker")
    update_data = LectureUpdate(name="New Name")

    with pytest.raises(HTTPException) as exc:
        await lecture_service.update_lecture(lecture_id, update_data, stranger)
    
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_lecture_success(lecture_service: LectureService) -> None:
    user_id = uuid4()
    lecture_id = uuid4()
    
    mock_lecture = MagicMock(spec=Lecture)
    mock_lecture.user_id = user_id
    lecture_service.lecture_crud.read.return_value = mock_lecture # type: ignore
    
    user = User(id=user_id, username="owner")
    await lecture_service.delete_lecture(lecture_id, user)
    
    lecture_service.lecture_crud.delete.assert_called_once_with(db_obj=mock_lecture) # type: ignore

@pytest.mark.asyncio
async def test_get_lecture_not_found(lecture_service: LectureService) -> None:
    lecture_service.lecture_crud.read.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lecture(uuid4())
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_lectures_page_invalid_sort(lecture_service: LectureService) -> None:
    # Проверка на недопустимое поле сортировки
    with pytest.raises(HTTPException) as exc:
        await lecture_service.get_lectures_page(
            page=1, limit=10, sort_by="illegal_field", order="desc", user_id=None
        )
    assert exc.value.status_code == 400
    assert "Invalid sort field" in exc.value.detail

@pytest.mark.asyncio
async def test_update_lecture_success(lecture_service: LectureService) -> None:
    # Проверка успешного обновления владельцем
    user_id = uuid4()
    lecture_id = uuid4()
    
    mock_lecture = MagicMock(spec=Lecture)
    mock_lecture.user_id = user_id
    lecture_service.lecture_crud.read.return_value = mock_lecture # type: ignore
    
    # Настраиваем возврат обновленного объекта
    updated_mock = MagicMock(spec=Lecture)
    lecture_service.lecture_crud.update.return_value = updated_mock # type: ignore
    
    user = User(id=user_id)
    update_data = LectureUpdate(name="Brand New Name")
    
    result = await lecture_service.update_lecture(lecture_id, update_data, user)
    
    lecture_service.lecture_crud.update.assert_called_once() # type: ignore
    assert result is not None

@pytest.mark.asyncio
async def test_update_lecture_not_found(lecture_service: LectureService) -> None:
    lecture_service.lecture_crud.read.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.update_lecture(uuid4(), LectureUpdate(name="?"), User(id=uuid4()))
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_lecture_access_denied(lecture_service: LectureService) -> None:
    # Мы проверили Update на доступ, но Delete — отдельный метод со своей проверкой
    owner_id = uuid4()
    stranger_id = uuid4()
    lecture_id = uuid4()
    
    mock_lecture = MagicMock(spec=Lecture)
    mock_lecture.user_id = owner_id
    lecture_service.lecture_crud.read.return_value = mock_lecture # type: ignore
    
    stranger = User(id=stranger_id)
    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_lecture(lecture_id, stranger)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_delete_lecture_not_found(lecture_service: LectureService) -> None:
    lecture_service.lecture_crud.read.return_value = None # type: ignore
    
    with pytest.raises(HTTPException) as exc:
        await lecture_service.delete_lecture(uuid4(), User(id=uuid4()))
    assert exc.value.status_code == 404