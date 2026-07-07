import re
from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

from api.logger import log

load_dotenv()

db_client: AsyncIOMotorClient = None

VENDOR_ADDRESS = getenv("VENDOR_ADDRESS", default="0x")
COMMISSION_SPLITTER_V2 = getenv("COMMISSION_SPLITTER_V2", default="0x")


def _mask_mongo_uri(uri: str) -> str:
    return re.sub(r"://[^@/]+@", "://***:***@", uri)


async def get_db() -> AsyncIOMotorClient:
    db_name = getenv("APP_MONGO_DB", default="example")
    if db_client is None:
        log.warning('Connection is None, nothing to get.')
        return
    return db_client[db_name]


async def connect_and_init_db():
    global db_client
    uri = getenv("APP_MONGO_URI", default="mongodb://localhost:27017")
    try:
        db_client = AsyncIOMotorClient(uri)
        server_info = await db_client.server_info()
        log.info(f"Connected to mongo! (version {server_info['version']}).")
    except Exception as e:
        log.error(
            f"Could not connect to mongo at {_mask_mongo_uri(uri)}: "
            f"{type(e).__name__}: {_mask_mongo_uri(str(e))}"
        )
        raise


async def close_db_connect():
    global db_client
    if db_client is None:
        log.warning('Connection is None, nothing to close.')
        return
    db_client.close()
    db_client = None
    log.info('Mongo connection closed.')

