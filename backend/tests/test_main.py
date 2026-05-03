import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Проверка базового эндпоинта /."""
    response = await client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    # Проверяем соответствие схеме Status
    assert data["status"] == "success"
    assert data["msg"] == "Health check OK"

@pytest.mark.asyncio
async def test_global_exception_handler_format(client: AsyncClient):
    """
    Проверяем, что при возникновении HTTPException 
    ответ прилетает в формате {"status": "error", "msg": "..."}
    """
    # Пытаемся получить лекцию, которой точно нет. 
    # В роутере это вызовет raise HTTPException(404, "Lecture not found")
    random_id = uuid4()
    response = await client.get(f"/lecture/{random_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    data = response.json()
    # Проверяем, что сработал именно твой кастомный обработчик из main.py
    assert data["status"] == "error"
    assert data["msg"] == "Lecture not found"

@pytest.mark.asyncio
async def test_validation_error_with_details(client: AsyncClient):
    """Проверка, что в msg теперь попадают конкретные ошибки валидации."""
    invalid_data = {
        "username": "u",        # Слишком короткий (min 3)
        "password": "1"         # Слишком короткий (min 6)
    }
    
    response = await client.post("/auth/register", json=invalid_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    data = response.json()
    assert data["status"] == "error"
    
    # Проверяем, что в строке ошибки есть упоминания обоих полей
    msg = data["msg"]
    assert "username" in msg
    assert "password" in msg
    # Пример ожидаемой строки: "Validation failed: username: String should have at least 3 characters | password: ..."