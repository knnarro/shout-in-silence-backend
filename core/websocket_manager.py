import asyncio

from fastapi import WebSocket

from core.redis_manager import RedisPubSubManager


class WebsocketManager:
    def __init__(self):
        self.active_connections = []
        self.pubsub_client = RedisPubSubManager()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.pubsub_client.connect()
        subscriber = await self.pubsub_client.subscribe("shout")
        asyncio.create_task(self._listen_pubsub(subscriber))

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await self.pubsub_client.unsubscribe("shout")

    async def broadcast(self, message: str):
        await self.pubsub_client.publish("shout", message)

    async def _listen_pubsub(self, subscriber):
        while True:
            message = await subscriber.get_message(ignore_subscribe_messages=True)
            if message is not None:
                for connection in self.active_connections:
                    await connection.send_text(message["data"].decode("utf-8"))
