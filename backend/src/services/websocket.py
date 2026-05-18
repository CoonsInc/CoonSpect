import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from redis.asyncio import Redis

from src.tasks.status import TaskStatus


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

        if ws is None:
            logger.warning(f"Disconnecting unknown task_id={task_id}")
            return

        try:
            await ws.close()
        except Exception as e:
            logger.warning(f"Error while disconnecting task_id={task_id}: {e}")
        logger.info(f"Disconnected task_id={task_id}")

    async def send_message(self, task_id: str, message: str) -> None:
        """Отправляет сообщение напрямую."""
        ws = self._connections.get(task_id)

        if ws is None:
            logger.debug(f"Cannot send to unknown task_id={task_id}")
            return

        try:
            logger.debug(
                f"Sent to {task_id}: "
                f"{message[:100] + '...' if len(message) > 100 else message}"
            )
            await ws.send_text(message)
        except WebSocketDisconnect:
            logger.warning(f"Client {task_id} disconnected during send")
            await self.disconnect(task_id)
        except Exception:
            logger.exception(f"Failed to send to {task_id}")

    def has_connection(self, task_id: str) -> bool:
        """Проверка наличия соединения."""
        return task_id in self._connections

    async def cleanup_all(self) -> None:
        """Массовое закрытие всех соединений (например, при выключении сервера)."""
        if not self._connections:
            return

        tasks = [self.disconnect(tid) for tid in list(self._connections.keys())]
        await asyncio.gather(*tasks)
        logger.info("All WebSocket connections cleaned up")


_wsmanager = WebSocketManager()


async def redis_updates_reader(redis: Redis):
    """Фоновый слушатель Redis Pub/Sub"""
    ws_manager = get_ws_manager()
    pubsub = redis.pubsub()
    await pubsub.subscribe("task_updates")
    try:
        async for message in pubsub.listen():
            logger.info(f"RECEIVED MSG FROM REDIS SUBPUB: {message}")
            if message["type"] == "message":
                task_id: str = message["data"]
                status_encoded: str | None = await redis.get(task_id)
                if status_encoded is None:
                    logger.error(f"task_id don't exist {task_id}")
                    continue
                status_decoded: dict[str, Any] = json.loads(status_encoded)
                if TaskStatus(status_decoded["status"]).is_final:
                    await redis.delete(task_id)
                await ws_manager.send_message(task_id, status_encoded)
    except asyncio.CancelledError:
        logger.info("redis_updates_reader shutting down...")
        raise
    finally:
        logger.error("redis_updates_reader is down")
        await pubsub.unsubscribe("task_updates")


def get_ws_manager() -> WebSocketManager:
    return _wsmanager
