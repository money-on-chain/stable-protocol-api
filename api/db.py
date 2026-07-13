import re
from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.collation import Collation
from dotenv import load_dotenv

from api.logger import log

load_dotenv()

db_client: AsyncIOMotorClient = None

VENDOR_ADDRESS = getenv("VENDOR_ADDRESS", default="0x")
COMMISSION_SPLITTER_V2 = getenv("COMMISSION_SPLITTER_V2", default="0x")

# Lets address queries match regardless of checksum casing while still
# being able to use an index (unlike a $regex/i scan of every document).
CASE_INSENSITIVE_COLLATION = Collation(locale="en", strength=2)

# (collection, index keys, extra create_index options)
_INDEX_SPECS = [
    ("Transaction", [("address", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION}),
    ("Transaction", [("tokenInvolved", 1), ("createdAt", -1)], {}),
    ("Transaction", [("event", 1), ("confirmationTime", 1)], {}),
    ("Transaction", [("otherAddress", 1)], {}),
    ("FastBtcBridge", [("rskAddress", 1), ("type", 1), ("timestamp", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION}),
]


def _mask_mongo_uri(uri: str) -> str:
    return re.sub(r"://[^@/]+@", "://***:***@", uri)


async def ensure_indexes():
    db_name = getenv("APP_MONGO_DB", default="example")
    db = db_client[db_name]
    for collection_name, keys, options in _INDEX_SPECS:
        try:
            await db[collection_name].create_index(keys, **options)
        except Exception as e:
            # Best-effort: the DB user may lack index-management privileges
            # (e.g. a read-only replica user), which shouldn't block startup.
            log.warning(
                f"Could not ensure index {keys} on {collection_name}: "
                f"{type(e).__name__}: {e}"
            )


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
        await ensure_indexes()
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

