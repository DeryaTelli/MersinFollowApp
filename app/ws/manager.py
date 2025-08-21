from collections import defaultdict
from typing import Dict, List
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.user_conns: Dict[int, List[WebSocket]] = defaultdict(list)
        self.admin_conns: List[WebSocket] = []

    async def connect_user(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.user_conns[user_id].append(ws)

    def disconnect_user(self, user_id: int, ws: WebSocket):
        if ws in self.user_conns.get(user_id, []):
            self.user_conns[user_id].remove(ws)

    async def connect_admin(self, ws: WebSocket):
        await ws.accept()
        self.admin_conns.append(ws)

    def disconnect_admin(self, ws: WebSocket):
        if ws in self.admin_conns:
            self.admin_conns.remove(ws)

    async def broadcast_to_admins(self, message: dict):
        dead = []
        for ws in self.admin_conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_admin(ws)

manager = WSManager()
