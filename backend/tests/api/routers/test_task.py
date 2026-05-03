import pytest
from fastapi.testclient import TestClient # Используем стандартный клиент для WS
from unittest.mock import AsyncMock, patch

from src.main import app # Или откуда у тебя импортируется объект FastAPI

# Создаем синхронный клиент специально для WS тестов
@pytest.fixture
def sync_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_start_task_api_success(client, sample_user, authorize_override):
    # Этот тест оставляем на AsyncClient, он работает отлично
    authorize_override(sample_user)
    fake_task_init = {"task_id": f"task:{sample_user.id}", "upload_url": "http://s3.url"}
    
    with patch("src.services.task.TaskService.start", new_callable=AsyncMock, return_value=fake_task_init):
        response = await client.post("/task/start")
        assert response.status_code == 200
        assert response.json()["task_id"] == fake_task_init["task_id"]
