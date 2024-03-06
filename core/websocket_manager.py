import json
import asyncio
import logging

from fastapi import WebSocket

from core.redis_manager import RedisPubSubManager

logger = logging.getLogger(__name__)


class WebsocketManager:
    def __init__(self):
        self.active_connections = []
        self.pubsub_client = RedisPubSubManager()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.pubsub_client.connect()
        subscriber = await self.pubsub_client.subscribe("shout")
        logger.info(f"Websocket connected {websocket}")
        asyncio.create_task(self._listen_and_send(subscriber, websocket))

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await self.pubsub_client.unsubscribe("shout")
        logger.info(f"Websocket disconnected {websocket}")

    async def broadcast(self, message: str):
        await self.pubsub_client.publish("shout", message)
        count = await self.pubsub_client.redis_connection.get("count")
        if not isinstance(count, bytes):
            await count
        await self.pubsub_client.redis_connection.set(
            "count", int(count.decode("utf-8")) + 1
        )

    async def _listen_and_send(self, subscriber, websocket):
        while True:
            message = await subscriber.get_message(ignore_subscribe_messages=True)
            if message is not None:
                count = await self.pubsub_client.redis_connection.get("count")
                if not isinstance(count, bytes):
                    await count
                body = json.loads(message["data"].decode("utf-8"))
                body["count"] = int(count.decode("utf-8"))
                await websocket.send_text(json.dumps(body))
