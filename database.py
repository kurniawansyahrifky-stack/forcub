from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

mongo = AsyncIOMotorClient(
    config("MONGO_URI")
)

db = mongo["menfess"]
users_db = db["users"]
premium_db = db["premium"]
