from motor.motor_asyncio import AsyncIOMotorClient

from core import settings

mongo_client = AsyncIOMotorClient(f"{settings.MONGO_HOST}:{settings.MONGO_PORT}")
mongo_db = mongo_client[settings.MONGO_DATABASE]
