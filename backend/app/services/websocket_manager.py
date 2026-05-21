from fastapi import WebSocket
from collections import defaultdict
from typing import DefaultDict, Set, Dict, Any
import orjson


class WebSocketManager:
    def __init__(self) -> None:
        self._rooms: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, run_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[run_id].add(websocket)

    def disconnect(self, run_id: str, websocket: WebSocket) -> None:
        self._rooms[run_id].discard(websocket)

    async def broadcast(self, run_id: str, event: Dict[str, Any]) -> None:
        sockets = list(self._rooms[run_id])
        payload = orjson.dumps(event).decode()
        for ws in sockets:
            try:
                await ws.send_text(payload)
            except Exception:
                self.disconnect(run_id, ws)


ws_manager = WebSocketManager()
