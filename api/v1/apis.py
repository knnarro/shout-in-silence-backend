import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.websocket_manager import WebsocketManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])
websocket_manager = WebsocketManager()


@router.websocket("/shout")
async def shout(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.broadcast(data)
    except WebSocketDisconnect as exc:
        await websocket_manager.disconnect(websocket)
        logger.exception(exc)
