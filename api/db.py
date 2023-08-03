from os import getenv
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

VENDOR_ADDRESS = getenv("VENDOR_ADDRESS", default="0x")
COMMISSION_SPLITTER_V2 = getenv("COMMISSION_SPLITTER_V2", default="0x")
client = motor.motor_asyncio.AsyncIOMotorClient(getenv("APP_MONGO_URI", default="mongodb://localhost:27017"))
db = client[getenv("APP_MONGO_DB", default="example")]
