from os import getenv
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(getenv("APP_MONGO_URI", default="mongodb://localhost:27017"))
db = client[getenv("APP_MONGO_DB", default="roc_mainnet")]
