import pytest
import uuid
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status as http_status
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect

from src.app.api.schemas.status import StatusType, Status


class TestCreateTaskEndpoint:
    """Тесты для GET /task/create"""
    
    def test_create_task_success(self, client, mock_external_dependencies):
        """Успешное создание задачи"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        with patch('uuid.uuid4', return_value=test_uuid):
            response = client.get("/task/create")
        
        assert response.status_code == 200
        assert response.json() == Status.success(str(test_uuid)).model_dump()
        
        # Проверяем Redis
        mock_external_dependencies['redis'].set.assert_called_once_with(
            f"task:{test_uuid}", "uploading"
        )
    
    def test_create_task_unique_ids(self, client, mock_external_dependencies):
        """Каждый вызов создает уникальный task_id"""
        uuids = [
            uuid.UUID('11111111-1111-1111-1111-111111111111'),
            uuid.UUID('22222222-2222-2222-2222-222222222222')
        ]
        
        with patch('uuid.uuid4', side_effect=uuids):
            response1 = client.get("/task/create")
            response2 = client.get("/task/create")
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["msg"] != data2["msg"]
        assert data1["msg"] == str(uuids[0])
        assert data2["msg"] == str(uuids[1])
        
        assert mock_external_dependencies['redis'].set.call_count == 2


class TestCheckTaskIdEndpoint:
    """Тесты для GET /task/correct/{task_id}"""
    
    def test_check_task_id_exists(self, client, mock_external_dependencies, sample_task_id):
        """Проверка существующего task_id"""
        mock_external_dependencies['redis'].exists.return_value = True
        
        response = client.get(f"/task/correct/{sample_task_id}")
        
        assert response.status_code == 200
        assert response.json() == Status.success().model_dump()
        
        # Проверяем правильный ключ
        mock_external_dependencies['redis'].exists.assert_called_once_with(
            f"task_status:{sample_task_id}"
        )
    
    def test_check_task_id_not_exists(self, client, mock_external_dependencies, sample_task_id):
        """Проверка несуществующего task_id"""
        mock_external_dependencies['redis'].exists.return_value = False
        
        response = client.get(f"/task/correct/{sample_task_id}")
        
        assert response.status_code == 400
        
        data = response.json()
        assert data["status"] == StatusType.ERROR.value
        assert data["msg"] == "Invalid task_id"


class TestStartTaskEndpoint:
    """Тесты для POST /task/start/{task_id}"""
    
    def test_start_task_success(self, client, mock_external_dependencies, sample_task_id):
        """Успешный запуск задачи"""
        mock_external_dependencies['redis'].exists.return_value = True
        
        response = client.post(
            f"/task/start/{sample_task_id}",
            files={"file": ("test_audio.wav", b"fake audio content", "audio/wav")}
        )
        
        assert response.status_code == 200
        assert response.json() == Status.success().model_dump()
        
        # Проверяем Redis
        mock_external_dependencies['redis'].exists.assert_called_once_with(
            f"task:{sample_task_id}"
        )
        
        # Проверяем что пайплайн запущен (просто проверяем что функция вызвалась)
        mock_external_dependencies['pipeline'].assert_called_once()
    
    def test_start_task_invalid_task_id(self, client, mock_external_dependencies, sample_task_id):
        """Запуск с несуществующим task_id"""
        mock_external_dependencies['redis'].exists.return_value = False
        
        response = client.post(
            f"/task/start/{sample_task_id}",
            files={"file": ("test.wav", b"content", "audio/wav")}
        )
        
        assert response.status_code == 400
        assert response.json() == Status.error("Invalid task_id").model_dump()
        
        # Проверяем что пайплайн НЕ запускался
        mock_external_dependencies['pipeline'].assert_not_called()
    
    def test_start_task_no_file(self, client, sample_task_id):
        """Запуск без файла"""
        response = client.post(f"/task/start/{sample_task_id}")
        
        assert response.status_code == 422  # FastAPI validation error
    
    def test_start_task_file_read_error(self, client, mock_external_dependencies, sample_task_id):
        """Ошибка при чтении файла"""
        mock_external_dependencies['redis'].exists.return_value = True
        
        # Имитируем ошибку в NamedTemporaryFile
        mock_external_dependencies['tempfile'].NamedTemporaryFile.side_effect = OSError("Disk full")
        
        response = client.post(
            f"/task/start/{sample_task_id}",
            files={"file": ("test.wav", b"content", "audio/wav")}
        )
        
        assert response.status_code == 400
        
        # Проверяем отправку ошибки в WebSocket
        mock_external_dependencies['manager'].send_message.assert_awaited_once_with(
            sample_task_id, "error: Disk full"
        )
        mock_external_dependencies['manager'].disconnect.assert_called_once_with(sample_task_id)
    
    def test_start_task_pipeline_error(self, client, mock_external_dependencies, sample_task_id):
        """Ошибка при запуске пайплайна"""
        mock_external_dependencies['redis'].exists.return_value = True
        
        # Устанавливаем side_effect для самой функции run_audio_pipeline_test
        mock_external_dependencies['pipeline'].side_effect = Exception("Pipeline failed")
        
        response = client.post(
            f"/task/start/{sample_task_id}",
            files={"file": ("test.wav", b"content", "audio/wav")}
        )
        
        assert response.status_code == 400
        
        # Проверяем отправку ошибки в WebSocket
        mock_external_dependencies['manager'].send_message.assert_awaited_once_with(
            sample_task_id, "error: Pipeline failed"
        )
        mock_external_dependencies['manager'].disconnect.assert_called_once_with(sample_task_id)


# Убрал pytest.mark.asyncio - тесты WebSocket запускаются через sync wrapper
class TestWebSocketEndpoint:
    """Тесты для WebSocket /task/ws/{task_id}"""
    
    # Тесты WebSocket сложно тестировать через TestClient, 
    # поэтому лучше их вынести в отдельные async тесты или использовать специальные инструменты
    
    def test_websocket_endpoint_exists(self, client):
        """Проверяем что WebSocket эндпоинт доступен"""
        # Просто проверяем что роутер зарегистрирован
        # Можно проверить что приложение имеет этот endpoint
        app = client.app
        websocket_routes = [route for route in app.routes if hasattr(route, 'path') and '/task/ws/' in route.path]
        assert len(websocket_routes) > 0


class TestTaskFlowIntegration:
    """Интеграционные тесты полного потока"""
    
    def test_complete_task_flow(self, client, mock_external_dependencies):
        """Полный поток: создание → проверка → запуск"""
        # 1. Создаем задачу
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        with patch('uuid.uuid4', return_value=test_uuid):
            create_response = client.get("/task/create")
            assert create_response.status_code == 200
            task_id = create_response.json()["msg"]
        
        # 2. Проверяем что задача существует
        # Настраиваем мок для task_status:{task_id}
        mock_external_dependencies['redis'].exists.return_value = True
        
        check_response = client.get(f"/task/correct/{task_id}")
        assert check_response.status_code == 200
        
        # 3. Запускаем задачу
        # Настраиваем мок для task:{task_id}
        mock_external_dependencies['redis'].exists.return_value = True
        
        start_response = client.post(
            f"/task/start/{task_id}",
            files={"file": ("audio.wav", b"audio data", "audio/wav")}
        )
        
        assert start_response.status_code == 200
        
        # Проверяем общую целостность
        # Redis должен был вызываться с правильными ключами
        mock_external_dependencies['redis'].set.assert_called_with(
            f"task:{task_id}", "uploading"
        )
