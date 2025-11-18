from typing import Dict
import asyncio
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, lecture_id: str):
        await websocket.accept()
        self.active_connections[lecture_id] = websocket
        print(f"[WS_MANAGER] Client connected to lecture {lecture_id}")
    
    def disconnect(self, lecture_id: str):
        if lecture_id in self.active_connections:
            del self.active_connections[lecture_id]
            print(f"[WS_MANAGER] Client disconnected from lecture {lecture_id}")
    
    async def send_message(self, lecture_id: str, message: str):
        if lecture_id in self.active_connections:
            try:
                websocket = self.active_connections[lecture_id]
                await websocket.send_text(message)
                print(f"[WS_MANAGER] Sent message to lecture {lecture_id}: {message}")
            except Exception as e:
                print(f"[WS_MANAGER] Error sending message to lecture {lecture_id}: {e}")
                self.disconnect(lecture_id)
        else:
            print(f"[WS_MANAGER] No active connection for lecture {lecture_id}")

manager = ConnectionManager()