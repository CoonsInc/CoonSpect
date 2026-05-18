import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.task import TaskInit
from src.services.task import TaskService
from src.tasks.status import TaskStatus


@pytest.fixture
def mock_s3() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def task_service(mock_s3, mock_redis) -> TaskService:
    return TaskService(s3_service=mock_s3, redis=mock_redis)


@pytest.fixture
def user():
    user_mock = MagicMock()
    user_mock.id = uuid4()
    return user_mock


@pytest.mark.asyncio
async def test_start_task_already_in_progress(task_service, mock_redis, user):
    """Тест: нельзя запустить задачу, если старая еще не завершена."""
    existing_status = json.dumps(
        {"status": TaskStatus.STT.value, "data": "Processing..."}
    )
    mock_redis.get.return_value = existing_status

    with pytest.raises(HTTPException) as exc:
        await task_service.start(user, original_filename="any")

    assert exc.value.status_code == 400
    assert "task in progress" in exc.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode, expected_patch",
    [
        ("prod", "src.tasks.tasks.run_audio_pipeline.kiq"),
        ("dev", "src.tasks.tasks_mock.run_audio_pipeline.kiq"),
    ],
)
async def test_start_task_success_logic(
    task_service, mock_s3, mock_redis, user, mode, expected_patch
):
    """Тест успешного цикла: инициализация и подтверждение старта."""
    mock_redis.get.side_effect = [None, b"test-file.mp3"]
    mock_s3.get_upload_url.return_value = "https://s3.url/upload"

    with (
        patch("src.services.task.settings") as mock_settings,
        patch(expected_patch, new_callable=AsyncMock) as mock_kiq,
        patch("src.services.task.update_status", new_callable=AsyncMock),
    ):
        mock_settings.BACKEND_MODE = mode
        mock_settings.S3_RAW_LECTURES_BUCKET = "test-bucket"
        mock_settings.ALLOWED_EXTENSIONS = {".mp3"}

        result = await task_service.start(user, original_filename="any.mp3")

        assert isinstance(result, TaskInit)
        assert result.task_id == f"task:{user.id}"
        assert result.upload_url == "https://s3.url/upload"

        mock_kiq.assert_not_called()

        await task_service.confirm_upload_and_start(result.task_id, user.id)

        mock_kiq.assert_called_once()


@pytest.mark.asyncio
async def test_ws_start_logic(task_service, mock_redis):
    """Тест ws_start: возвращает JSON для активных и удаляет из Redis завершенные."""
    task_id = "task:test"

    active_data = {"status": TaskStatus.STT.value, "data": "working"}
    mock_redis.get.return_value = json.dumps(active_data)

    res = await task_service.ws_start(task_id)
    assert json.loads(res) == active_data

    final_data = {"status": TaskStatus.FINISH.value, "data": "done"}
    mock_redis.get.return_value = json.dumps(final_data)

    res = await task_service.ws_start(task_id)
    assert res is None
    mock_redis.delete.assert_called_once_with(task_id)


@pytest.mark.asyncio
async def test_get_task_status_complex(task_service, mock_redis):
    """Тест получения статуса с фильтрацией финальных состояний."""
    task_id = "task:123"

    mock_redis.get.return_value = None
    assert await task_service.get_task_status(task_id) is None

    mock_redis.get.return_value = json.dumps(
        {"status": TaskStatus.ERROR.value, "data": "rip"}
    )
    assert await task_service.get_task_status(task_id) is None

    mock_redis.get.return_value = json.dumps(
        {"status": TaskStatus.STARTING.value, "data": "ok"}
    )
    status = await task_service.get_task_status(task_id)
    assert status["status"] == TaskStatus.STARTING.value
