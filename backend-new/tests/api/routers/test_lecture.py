import pytest
from httpx import AsyncClient
from uuid import uuid4
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.sql.models.user import User
from src.infra.sql.models.lecture import Lecture

@pytest.fixture
async def sample_lecture(db_session: AsyncSession, sample_user: User) -> Lecture:
    lecture = Lecture(
        id=uuid4(), 
        name="Base Lecture", 
        text="Content", 
        user_id=sample_user.id
    )
    db_session.add(lecture)
    await db_session.commit()
    await db_session.refresh(lecture)
    return lecture

@pytest.mark.asyncio
async def test_get_lecture_by_id(
    client: AsyncClient, 
    sample_lecture: Lecture
) -> None:
    """Тест получения конкретной лекции по ID."""
    response = await client.get(f"/lecture/{sample_lecture.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(sample_lecture.id)
    assert data["name"] == "Base Lecture"

@pytest.mark.asyncio
async def test_get_lectures_list_pagination(
    client: AsyncClient, 
    db_session: AsyncSession, 
    sample_user: User
) -> None:
    """Тест списка лекций с пагинацией (LecturesPage)."""
    # Создаем 5 лекций
    for i in range(5):
        db_session.add(Lecture(id=uuid4(), name=f"L {i}", text="...", user_id=sample_user.id))
    await db_session.commit()

    # Запрашиваем 2-ю страницу по 2 элемента
    response = await client.get("/lecture/list?page=2&limit=2")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Проверяем структуру LecturesPage (обычно это dict с items и total)
    assert "items" in data
    assert len(data["items"]) == 2
    assert "total" in data

@pytest.mark.asyncio
async def test_edit_lecture_success(
    client: AsyncClient, 
    sample_user: User, 
    sample_lecture: Lecture, 
    authorize_override
) -> None:
    """Тест успешного редактирования своей лекции."""
    authorize_override(sample_user)
    
    update_payload = {"name": "Updated Name"}
    response = await client.patch(f"/lecture/edit/{sample_lecture.id}", json=update_payload)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_delete_lecture_forbidden(
    client: AsyncClient, 
    db_session: AsyncSession, 
    authorize_override
) -> None:
    """Тест: юзер не может удалить чужую лекцию."""
    # 1. Создаем "чужого" юзера и его лекцию
    other_user = User(id=uuid4(), username="stranger", password_hash="...")
    foreign_lecture = Lecture(id=uuid4(), name="Not Yours", text="...", user_id=other_user.id)
    db_session.add_all([other_user, foreign_lecture])
    await db_session.commit()

    # 2. Авторизуем "нашего" юзера
    me = User(id=uuid4(), username="me", password_hash="...")
    db_session.add(me)
    await db_session.commit()
    authorize_override(me)

    # 3. Пытаемся удалить чужое
    response = await client.delete(f"/lecture/delete/{foreign_lecture.id}")
    
    # Сервис должен выбросить 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_delete_lecture_success(
    client: AsyncClient, 
    sample_user: User, 
    sample_lecture: Lecture, 
    authorize_override
) -> None:
    """Тест успешного удаления своей лекции."""
    authorize_override(sample_user)
    
    response = await client.delete(f"/lecture/delete/{sample_lecture.id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success" # Проверка схемы Status