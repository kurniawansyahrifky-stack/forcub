from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

mongo = AsyncIOMotorClient(
    config("MONGO_URI")
)

db = mongo["menfess"]

premium_db = db["premium"]
