import pytest
import json
from uuid import uuid4
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.task import TaskService
from src.tasks.status import TaskStatus
from src.api.schemas.task import TaskInit

@pytest.fixture
def mock_s3():
    return AsyncMock()

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def task_service(mock_s3, mock_redis):
    return TaskService(s3_service=mock_s3, redis=mock_redis)

@pytest.fixture
def user():
    user_mock = MagicMock()
    user_mock.id = uuid4()
    return user_mock

@pytest.mark.asyncio
async def test_start_task_already_in_progress(task_service, mock_redis, user):
    """Тест: нельзя запустить задачу, если старая еще не завершена."""
    existing_status = json.dumps({
        "status": TaskStatus.STT.value, 
        "data": "Processing..."
    })
    mock_redis.get.return_value = existing_status

    with pytest.raises(HTTPException) as exc:
        await task_service.start(user)
    
    assert exc.value.status_code == 400
    assert "task in progress" in exc.value.detail

@pytest.mark.asyncio
@pytest.mark.parametrize("mode, expected_patch", [
    ("prod", "src.tasks.tasks.run_audio_pipeline.kiq"),
    ("dev", "src.tasks.tasks_mock.run_audio_pipeline.kiq"),
])
async def test_start_task_success_logic(task_service, mock_s3, mock_redis, user, mode, expected_patch):
    """Тест успешного старта: проверяем S3 URL, Redis и правильный kiq пайплайн."""
    mock_redis.get.return_value = None
    mock_s3.get_upload_url.return_value = "https://s3.url/upload"
    
    # Мокаем настройки и пайплайны
    with patch("src.services.task.settings") as mock_settings, \
         patch(expected_patch, new_callable=AsyncMock) as mock_kiq, \
         patch("src.services.task.update_status", new_callable=AsyncMock) as mock_update:
        
        mock_settings.BACKEND_MODE = mode
        mock_settings.S3_RAW_LECTURES_BUCKET = "test-bucket"

        result = await task_service.start(user)

        # Проверки
        assert isinstance(result, TaskInit)
        assert result.task_id == f"task:{user.id}"
        assert result.upload_url == "https://s3.url/upload"
        
        mock_kiq.assert_called_once()
        mock_update.assert_called_once_with(mock_redis, f"task:{user.id}", TaskStatus.STARTING)

@pytest.mark.asyncio
async def test_ws_start_logic(task_service, mock_redis):
    """Тест ws_start: возвращает JSON для активных и удаляет из Redis завершенные."""
    task_id = "task:test"
    
    # 1. Активная задача
    active_data = {"status": TaskStatus.STT.value, "data": "working"}
    mock_redis.get.return_value = json.dumps(active_data)
    
    res = await task_service.ws_start(task_id)
    assert json.loads(res) == active_data

    # 2. Завершенная задача (должна быть удалена)
    final_data = {"status": TaskStatus.FINISH.value, "data": "done"}
    mock_redis.get.return_value = json.dumps(final_data)
    
    res = await task_service.ws_start(task_id)
    assert res is None
    mock_redis.delete.assert_called_once_with(task_id)

@pytest.mark.asyncio
async def test_get_task_status_complex(task_service, mock_redis):
    """Тест получения статуса с фильтрацией финальных состояний."""
    task_id = "task:123"
    
    # Если в Redis пусто
    mock_redis.get.return_value = None
    assert await task_service.get_task_status(task_id) is None

    # Если задача в финальном статусе (например, ERROR)
    mock_redis.get.return_value = json.dumps({"status": TaskStatus.ERROR.value, "data": "rip"})
    assert await task_service.get_task_status(task_id) is None

    # Если задача активна
    mock_redis.get.return_value = json.dumps({"status": TaskStatus.STARTING.value, "data": "ok"})
    status = await task_service.get_task_status(task_id)
    assert status["status"] == TaskStatus.STARTING.value