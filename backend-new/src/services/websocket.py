from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

class WebSocketManager:
    """Менеджер WebSocket-соединений."""
    
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str) -> bool:
        """Принимает соединение и регистрирует его."""
        await websocket.accept()
        if task_id in self._connections:
            await websocket.close(code=4000, reason="Task already connected")
            logger.warning(f"Duplicate connection attempt for task_id={task_id}")
            return False
        
        self._connections[task_id] = websocket
        logger.info(f"Connected task_id={task_id}")
        return True
    
    async def disconnect(self, task_id: str) -> None:
        """Закрывает и удаляет соединение."""
        ws = self._connections.pop(task_id, None)
        if ws:
            try:
                await ws.close()
            except Exception as e:
                logger.warning(f"Error while disconnecting task_id={task_id}: {e}")
            logger.info(f"Disconnected task_id={task_id}")
        else:
            logger.warning(f"Disconnecting unknown task_id={task_id}")
    
    async def send_message(self, task_id: str, message: str) -> None:
        """Отправляет сообщение напрямую."""
        ws = self._connections.get(task_id)
        
        if ws is None:
            logger.debug(f"Cannot send to unknown task_id={task_id}")
            return
        
        try:
            await ws.send_text(message)
            logger.debug(f"Sent to {task_id}: {message[:100]}...")
        except WebSocketDisconnect:
            logger.warning(f"Client {task_id} disconnected during send")
            await self.disconnect(task_id)
        except Exception:
            logger.exception(f"Failed to send to {task_id}")
    
    def has_connection(self, task_id: str) -> bool:
        """Проверка наличия соединения."""
        return task_id in self._connections
    
    async def cleanup_all(self) -> None:
        """Закрывает все соединения."""
        for task_id in list(self._connections.keys()):
            await self.disconnect(task_id)
        logger.info("All WebSocket connections closed")

wsmanager = WebSocketManager()