import pytest
from unittest.mock import AsyncMock
from src.services.websocket import WebSocketManager
from fastapi import WebSocketDisconnect

@pytest.mark.asyncio
async def test_connect_success(ws_manager: WebSocketManager):
    # Создаем мок для WebSocket
    mock_ws = AsyncMock()
    task_id = "test_task_1"
    
    result = await ws_manager.connect(mock_ws, task_id)
    
    assert result is True
    assert ws_manager.has_connection(task_id) is True
    mock_ws.accept.assert_called_once()

@pytest.mark.asyncio
async def test_connect_duplicate_fails(ws_manager: WebSocketManager):
    mock_ws_1 = AsyncMock()
    mock_ws_2 = AsyncMock()
    task_id = "duplicate_task"
    
    # Первое подключение
    await ws_manager.connect(mock_ws_1, task_id)
    
    # Второе подключение с тем же ID
    result = await ws_manager.connect(mock_ws_2, task_id)
    
    assert result is False
    # Проверяем, что второе соединение закрыто со специфическим кодом
    mock_ws_2.close.assert_called_once_with(code=4000, reason="Task already connected")

@pytest.mark.asyncio
async def test_disconnect(ws_manager: WebSocketManager):
    mock_ws = AsyncMock()
    task_id = "to_be_removed"
    
    await ws_manager.connect(mock_ws, task_id)
    await ws_manager.disconnect(task_id)
    
    assert ws_manager.has_connection(task_id) is False
    mock_ws.close.assert_called_once()

@pytest.mark.asyncio
async def test_send_message_success(ws_manager: WebSocketManager):
    mock_ws = AsyncMock()
    task_id = "msg_task"
    message = "Hello, World!"
    
    await ws_manager.connect(mock_ws, task_id)
    await ws_manager.send_message(task_id, message)
    
    mock_ws.send_text.assert_called_once_with(message)

@pytest.mark.asyncio
async def test_send_message_disconnect_handling(ws_manager: WebSocketManager):
    mock_ws = AsyncMock()
    # Имитируем разрыв соединения при отправке
    mock_ws.send_text.side_effect = WebSocketDisconnect()
    task_id = "dead_link"
    
    await ws_manager.connect(mock_ws, task_id)
    await ws_manager.send_message(task_id, "test")
    
    # Должен сработать disconnect и удалить связь
    assert ws_manager.has_connection(task_id) is False

@pytest.mark.asyncio
async def test_cleanup_all(ws_manager: WebSocketManager):
    tasks = ["t1", "t2", "t3"]
    for t in tasks:
        await ws_manager.connect(AsyncMock(), t)
    
    await ws_manager.cleanup_all()
    
    for t in tasks:
        assert ws_manager.has_connection(t) is False
