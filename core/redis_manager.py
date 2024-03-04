import redis.asyncio as aioredis

from core import settings


class RedisPubSubManager:
    def __init__(self):
        self.redis_host = settings.REDIS_HOST
        self.redis_port = settings.REDIS_PORT
        self.redis_connection = None
        self.pubsub = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        return aioredis.Redis(host=self.redis_host, port=self.redis_port)

    async def connect(self) -> None:
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, channel: str, message: str) -> None:
        await self.redis_connection.publish(channel, message)

    async def subscribe(self, channel: str) -> aioredis.Redis.pubsub:
        await self.pubsub.subscribe(channel)
        return self.pubsub

    async def unsubscribe(self, channel: str) -> None:
        await self.pubsub.unsubscribe(channel)
