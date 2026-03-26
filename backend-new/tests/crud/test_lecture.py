import pytest
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.lecture import LectureCRUD
from src.infra.sql.models.lecture import Lecture
from src.infra.sql.models.user import User

@pytest.fixture
async def lecture_crud(db_session: AsyncSession) -> LectureCRUD:
    return LectureCRUD(db_session)

@pytest.mark.asyncio
async def test_get_list_pagination_logic(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    # Добавлено обязательное поле text
    lectures: list[Lecture] = [
        Lecture(
            id=uuid4(), 
            name=f"Lec {i}", 
            user_id=sample_user.id, 
            text=f"Content {i}"
        )
        for i in range(5)
    ]
    db_session.add_all(lectures)
    await db_session.commit()

    items, total, pages = await lecture_crud.get_list(page=1, limit=2)
    assert total == 5
    assert pages == 3
    assert len(items) == 2

    items, total, pages = await lecture_crud.get_list(page=3, limit=2)
    assert len(items) == 1
    
    items, total, pages = await lecture_crud.get_list(page=99, limit=2)
    assert items == []

@pytest.mark.asyncio
async def test_get_list_sorting(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    # Добавлено поле text
    l1 = Lecture(id=uuid4(), name="AAA", user_id=sample_user.id, text="some text")
    l2 = Lecture(id=uuid4(), name="ZZZ", user_id=sample_user.id, text="other text")
    db_session.add_all([l1, l2])
    await db_session.commit()

    items, _, _ = await lecture_crud.get_list(sort_by="name", order="asc")
    assert items[0].name == "AAA"

    items, _, _ = await lecture_crud.get_list(sort_by="name", order="desc")
    assert items[0].name == "ZZZ"

@pytest.mark.asyncio
async def test_get_list_filter_by_user(
    lecture_crud: LectureCRUD, 
    db_session: AsyncSession
) -> None:
    u1_id: UUID = uuid4()
    u2_id: UUID = uuid4()
    
    # Исправлено имя поля: password_hash
    db_session.add_all([
        User(id=u1_id, username="u1", password_hash="."),
        User(id=u2_id, username="u2", password_hash=".")
    ])
    
    # Добавлено поле text
    db_session.add(Lecture(id=uuid4(), name="U1 Lec", user_id=u1_id, text="t1"))
    db_session.add(Lecture(id=uuid4(), name="U2 Lec", user_id=u2_id, text="t2"))
    await db_session.commit()

    items, total, _ = await lecture_crud.get_list(user_id=u1_id)
    assert total == 1
    assert items[0].name == "U1 Lec"

@pytest.mark.asyncio
async def test_get_list_joinedload_user(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    # Добавлено поле text
    lec = Lecture(id=uuid4(), name="Joined Lec", user_id=sample_user.id, text="joined text")
    db_session.add(lec)
    await db_session.commit()

    items, _, _ = await lecture_crud.get_list(limit=1)
    assert items[0].user.username == sample_user.username

@pytest.mark.asyncio
async def test_create_lecture(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    # Данные для создания
    lecture_data = {
        "name": "New Architecture",
        "text": "History of Roman architecture",
        "lecturer": "Dr. Smith",
        "user_id": sample_user.id
    }
    
    # Тестируем метод create (из BaseCRUD)
    db_obj = await lecture_crud.create(obj_in=lecture_data)
    
    assert db_obj.id is not None
    assert db_obj.name == "New Architecture"
    assert db_obj.user_id == sample_user.id

@pytest.mark.asyncio
async def test_read_lecture(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    # Сначала создаем запись в БД
    lec = Lecture(id=uuid4(), name="Read Me", text="Some text", user_id=sample_user.id)
    db_session.add(lec)
    await db_session.commit()

    # Тестируем метод read (из BaseCRUD)
    found_obj = await lecture_crud.read(id=lec.id)
    
    assert found_obj is not None
    assert found_obj.name == "Read Me"
    
    # Проверка на несуществующий ID
    not_found = await lecture_crud.read(id=uuid4())
    assert not_found is None

@pytest.mark.asyncio
async def test_update_lecture_fields(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    lec = Lecture(id=uuid4(), name="Old Name", text="Old Text", user_id=sample_user.id)
    db_session.add(lec)
    await db_session.commit()

    # Тестируем метод update (из BaseCRUD) через словарь
    update_data = {"name": "Updated Name"}
    updated_obj = await lecture_crud.update(db_obj=lec, update_data=update_data)
    
    assert updated_obj.name == "Updated Name"
    assert updated_obj.text == "Old Text"  # Поле не должно было измениться

@pytest.mark.asyncio
async def test_delete_lecture(
    lecture_crud: LectureCRUD, 
    sample_user: User, 
    db_session: AsyncSession
) -> None:
    lec = Lecture(id=uuid4(), name="To Delete", text="...", user_id=sample_user.id)
    db_session.add(lec)
    await db_session.commit()

    # Тестируем метод delete (из BaseCRUD)
    result = await lecture_crud.delete(db_obj=lec)
    assert result is True
    
    # Проверяем, что в базе пусто
    found = await lecture_crud.read(id=lec.id)
    assert found is None