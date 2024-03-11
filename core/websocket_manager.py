import json
import asyncio
import logging

from fastapi import WebSocket

from core.mongodb import mongo_db
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
        await self.pubsub_client.increase("count")
        await self.pubsub_client.publish("shout", message)
        await mongo_db["messages"].insert_one(json.loads(message))

    async def _listen_and_send(self, subscriber, websocket):
        while True:
            message = await subscriber.get_message(ignore_subscribe_messages=True)
            if message is not None:
                count = await self.pubsub_client.get("count")
                count = int(count) if count else 0
                body = json.loads(message["data"].decode("utf-8"))
                body["count"] = count
                await websocket.send_text(json.dumps(body))
