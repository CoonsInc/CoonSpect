import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import uuid
from fastapi import WebSocketDisconnect

from src.app.main import app

@pytest.fixture
def client():
    """Тестовый клиент FastAPI"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Автоматически мокаем все внешние зависимости"""
    with patch('src.app.api.routers.tasks.r') as mock_redis, \
         patch('src.app.api.routers.tasks.manager') as mock_manager, \
         patch('src.app.api.routers.tasks.run_audio_pipeline_test') as mock_pipeline, \
         patch('src.app.api.routers.tasks.run_audio_pipeline') as mock_pipeline_real, \
         patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
         patch('builtins.print') as mock_print, \
         patch('src.app.api.routers.tasks.manager.send_message') as mock_send_msg, \
         patch('src.app.api.routers.tasks.manager.disconnect') as mock_disconnect:
        
        # Настраиваем мок Redis
        mock_redis.set = Mock()
        mock_redis.exists = Mock(return_value=True)
        
        # Настраиваем мок менеджера WebSocket
        mock_manager.connect = AsyncMock()
        mock_manager.send_message = AsyncMock()
        mock_manager.disconnect = Mock()
        
        # Настраиваем мок пайплайна (функция, а не метод с apply_async!)
        # Ваша функция вызывается как run_audio_pipeline_test(task_id, path)
        mock_pipeline.return_value = None  # Просто возвращает None
        
        # Настраиваем мок временных файлов
        mock_tempfile_context = Mock()
        mock_tempfile_context.name = "/tmp/test_file.wav"
        mock_tempfile_context.write = Mock()
        mock_tempfile_context.__enter__ = Mock(return_value=mock_tempfile_context)
        mock_tempfile_context.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tempfile_context
        
        yield {
            'redis': mock_redis,
            'manager': mock_manager,
            'pipeline': mock_pipeline,  # Это функция, а не объект с apply_async
            'tempfile': mock_tempfile,
            'print': mock_print,
            'send_message': mock_send_msg,
            'disconnect': mock_disconnect
        }

@pytest.fixture
def sample_task_id():
    """Пример task_id для тестов"""
    return "12345678-1234-5678-1234-567812345678"

@pytest.fixture
def mock_websocket():
    """Мок WebSocket соединения"""
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()
    mock_ws.receive_text = AsyncMock(side_effect=WebSocketDisconnect())
    mock_ws.close = AsyncMock()
    return mock_ws
