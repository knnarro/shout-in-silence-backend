from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from connect_manager import ConnectionManager

router = APIRouter(prefix="/api/v1", tags=["v1"])
manager = ConnectionManager()


@router.websocket("/shout")
async def shout(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
