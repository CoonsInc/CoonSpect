import pytest
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.lecture import get_list, get_by_id, create, update, delete
from src.infra.sql.models.lecture import Lecture
from src.infra.sql.models.user import User
from src.api.schemas.lecture import LectureCreate, LectureUpdate

@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Создает пользователя для привязки лекций."""
    user = User(id=uuid4(), username="lecturer", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_create_lecture(db_session: AsyncSession, sample_user: User):
    """Проверка создания лекции через DTO LectureCreate."""
    # sample_user.id теперь типизирован как uuid.UUID благодаря Mapped
    user_uuid = sample_user.id 
    
    lecture_in = LectureCreate(
        user_id=user_uuid,
        name="Async Physics",
        lecturer="Dr. Smith",
        audio_url="http://example.com/audio.mp3",
        text="Very complex stuff"
    )
    
    lecture = await create(db_session, lecture_in)
    
    # Больше никаких cast! Mapped[str] делает свое дело.
    assert lecture.id is not None
    assert lecture.name == "Async Physics"
    assert lecture.text == "Very complex stuff"
    assert lecture.user_id == user_uuid

@pytest.mark.asyncio
async def test_get_lecture_by_id(db_session: AsyncSession, sample_user: User):
    """Проверка получения лекции по ID."""
    new_lec = Lecture(
        name="Math", 
        text="1+1=2", 
        lecturer="Newton", 
        user_id=sample_user.id
    )
    db_session.add(new_lec)
    await db_session.commit()
    
    # Если get_by_id аннотирован как -> Lecture | None, cast не нужен
    found = await get_by_id(db_session, new_lec.id)
    
    assert found is not None
    assert found.name == "Math"
    assert found.lecturer == "Newton"

@pytest.mark.asyncio
async def test_get_list_pagination(db_session: AsyncSession, sample_user: User):
    """Проверка пагинации и joinedload пользователя."""
    for i in range(5):
        db_session.add(Lecture(
            name=f"Lec {i}", 
            text="...", 
            lecturer="Proff", 
            user_id=sample_user.id
        ))
    await db_session.commit()
    
    items, total, pages = await get_list(db_session, page=1, limit=2)
    
    assert len(items) == 2
    assert total == 5
    assert pages == 3
    # Mapped["User"] в модели Lecture позволяет обращаться к user.username напрямую
    assert items[0].user.username == "lecturer"

@pytest.mark.asyncio
async def test_update_lecture(db_session: AsyncSession, sample_user: User):
    """Проверка частичного обновления через LectureUpdate."""
    lec = Lecture(name="Old Title", text="Old Content", user_id=sample_user.id)
    db_session.add(lec)
    await db_session.commit()
    
    update_data = LectureUpdate(name="New Title")
    updated_lec = await update(db_session, lec, update_data)
    
    assert updated_lec.name == "New Title"
    assert updated_lec.text == "Old Content"

@pytest.mark.asyncio
async def test_delete_lecture(db_session: AsyncSession, sample_user: User):
    """Проверка удаления лекции."""
    lec = Lecture(name="To be deleted", text="...", user_id=sample_user.id)
    db_session.add(lec)
    await db_session.commit()
    
    result = await delete(db_session, lec)
    assert result is True
    
    check = await get_by_id(db_session, lec.id)
    assert check is None
    