from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.infra.db.models.user import User
from src.main import app


@pytest.fixture
def sync_client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_confirm_task_api_success(
    client: AsyncClient, sample_user: User, authorize_override
):
    """Тест API подтверждения загрузки и запуска обработки."""
    authorize_override(sample_user)

    expected_task_id = f"task:{sample_user.id}"

    with (
        patch(
            "src.services.task.TaskService.get_task_id", return_value=expected_task_id
        ),
        patch(
            "src.services.task.TaskService.confirm_upload_and_start",
            new_callable=AsyncMock,
        ) as mock_confirm,
    ):
        response = await client.post("/task/confirm")

        assert response.status_code == 200
        assert response.json() == {"status": "processing_started"}

        mock_confirm.assert_called_once_with(expected_task_id, sample_user.id)
