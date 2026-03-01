from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket
    
    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    def contains(self, task_id: str) -> bool:
        return self.active_connections.get(task_id) != None
    
    async def send_message(self, task_id: str, message: str):
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_text(message)

manager = ConnectionManager()
