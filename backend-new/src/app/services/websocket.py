# websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Асинхронно-безопасный менеджер WebSocket-соединений."""
    
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()  # 🔒 защита от гонок в асинх-контексте
    
    async def connect(self, websocket: WebSocket, task_id: str) -> bool:
        """
        Принимает соединение и регистрирует его.
        Возвращает False, если task_id уже занят.
        """
        await websocket.accept()
        async with self._lock:
            if task_id in self._connections:
                # Уже есть активное соединение — отклоняем новое
                await websocket.close(code=4000, reason="Task already connected")
                logger.warning(f"Duplicate connection attempt for task_id={task_id}")
                return False
            self._connections[task_id] = websocket
            logger.info(f"Connected task_id={task_id}")
            return True
    
    async def disconnect(self, task_id: str) -> None:
        """Безопасно закрывает и удаляет соединение."""
        async with self._lock:
            ws = self._connections.pop(task_id, None)
            if ws:
                try:
                    await ws.close()
                except RuntimeError:
                    # Сокет уже закрыт — это нормально
                    pass
                logger.info(f"Disconnected task_id={task_id}")
    
    async def send_message(self, task_id: str, message: str) -> bool:
        """
        Отправляет сообщение. Возвращает True если успешно, False если соединения нет.
        """
        async with self._lock:
            ws = self._connections.get(task_id)
        
        if ws is None:
            logger.debug(f"Cannot send to unknown task_id={task_id}")
            return False
        
        try:
            await ws.send_text(message)
            logger.debug(f"Sent to {task_id}: {message[:100]}...")
            return True
        except WebSocketDisconnect:
            logger.warning(f"Client {task_id} disconnected during send")
            # Чистим "зомби"-соединение
            await self.disconnect(task_id)
            return False
        except Exception as e:
            logger.error(f"Failed to send to {task_id}: {e}")
            return False
    
    def has_connection(self, task_id: str) -> bool:
        """Проверка наличия соединения (без блокировки, для чтения)."""
        return task_id in self._connections
    
    async def cleanup_all(self) -> None:
        """Закрывает все соединения — полезно при завершении приложения."""
        async with self._lock:
            for task_id, ws in list(self._connections.items()):
                try:
                    await ws.close()
                except Exception:
                    pass
            self._connections.clear()
        logger.info("All WebSocket connections closed")

manager = WebSocketManager()