import redis.asyncio as aioredis

from core import settings


class RedisPubSubManager:
    def __init__(self):
        self.redis_host: str = settings.REDIS_HOST
        self.redis_port: int = settings.REDIS_PORT
        self.redis_connection: aioredis.Redis | None = None
        self.pubsub: aioredis.Redis.pubsub = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        return aioredis.Redis(host=self.redis_host, port=self.redis_port)

    async def connect(self) -> None:
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, channel: str, message: str) -> None:
        await self.redis_connection.publish(channel, message)

    async def increase(self, channel: str) -> None:
        await self.redis_connection.incr(channel)

    async def get(self, channel: str) -> any:
        return await self.redis_connection.get(channel)

    async def set(self, channel: str, value: any) -> None:
        await self.redis_connection.set(channel, value)

    async def subscribe(self, channel: str) -> aioredis.Redis.pubsub:
        await self.pubsub.subscribe(channel)
        return self.pubsub

    async def unsubscribe(self, channel: str) -> None:
        await self.pubsub.unsubscribe(channel)
