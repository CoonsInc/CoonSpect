from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, task_id: int):
        await websocket.accept()
        self.active_connections[task_id] = websocket
    
    def disconnect(self, task_id: int):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
    
    async def send_message(self, task_id: str, message: str):
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_text(message)

manager = ConnectionManager()