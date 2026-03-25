import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import get_by_username, get_by_id, create
from src.infra.sql.models.user import User

@pytest.mark.asyncio
async def test_get_by_username_found(db_session: AsyncSession):
    """Проверка поиска существующего пользователя в БД."""
    # 1. Сначала создаем пользователя напрямую
    username = "test_user"
    new_user = User(username=username, password_hash="hashed_stuff")
    db_session.add(new_user)
    await db_session.commit()

    # 2. Пытаемся его найти через CRUD
    result = await get_by_username(db_session, username)

    # Линтер понимает типы из Mapped, проверки проходят чисто
    assert result is not None
    assert result.username == username
    assert result.id == new_user.id

@pytest.mark.asyncio
async def test_get_by_username_not_found(db_session: AsyncSession):
    """Проверка поиска несуществующего пользователя."""
    result = await get_by_username(db_session, "non_existent")
    assert result is None

@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession):
    """Проверка поиска пользователя по его UUID."""
    user_uuid = uuid4()
    new_user = User(id=user_uuid, username="uuid_user", password_hash="hashed")
    db_session.add(new_user)
    await db_session.commit()

    result = await get_by_id(db_session, user_uuid)

    assert result is not None
    assert result.id == user_uuid
    assert result.username == "uuid_user"

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Проверка создания пользователя через CRUD (с проверкой хэша)."""
    username = "new_user"
    password = "secret_password"

    # Вызываем создание
    user = await create(db_session, username, password)

    # Проверяем, что объект вернулся с ID
    assert user.id is not None
    assert user.username == username
    
    # Проверяем хэш пароля
    assert user.password_hash != password
    assert len(user.password_hash) > 10

    # Дополнительно: проверяем, что он реально в базе
    db_user = await get_by_id(db_session, user.id)
    assert db_user is not None
    assert db_user.username == username
