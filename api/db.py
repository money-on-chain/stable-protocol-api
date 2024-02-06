from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

from api.logger import log

load_dotenv()

db_client: AsyncIOMotorClient = None

VENDOR_ADDRESS = getenv("VENDOR_ADDRESS", default="0x")
COMMISSION_SPLITTER_V2 = getenv("COMMISSION_SPLITTER_V2", default="0x")


async def get_db() -> AsyncIOMotorClient:
    db_name = getenv("APP_MONGO_DB", default="example")
    if db_client is None:
        log.warning('Connection is None, nothing to get.')
        return
    return db_client[db_name]


async def connect_and_init_db():
    global db_client
    try:
        db_client = AsyncIOMotorClient(getenv("APP_MONGO_URI", default="mongodb://localhost:27017"))
        log.info('Connected to mongo.')
    except Exception as e:
        log.exception(f'Could not connect to mongo: {e}')
        raise


async def close_db_connect():
    global db_client
    if db_client is None:
        log.warning('Connection is None, nothing to close.')
        return
    db_client.close()
    db_client = None
    log.info('Mongo connection closed.')

