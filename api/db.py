import asyncio
import re
from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.collation import Collation
from dotenv import load_dotenv

from api.logger import log

load_dotenv()

db_client: AsyncIOMotorClient = None

# Kept alive so it isn't garbage-collected mid-flight; see ensure_indexes()
# scheduling note in connect_and_init_db().
_index_task: asyncio.Task = None

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
    ("event_VestingFactory_VestingCreated",
     [("holder", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION}),
    ("event_IncentiveV2_ClaimOK", [("recipient", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION}),
]

# Some OMoC event feeds accept an optional address filter that "$or"s the
# address against every party field on the event (api/routers/omoc.py), so
# index each of those fields (with the createdAt sort key) under the same
# case-insensitive collation the query uses.
_ADDRESS_FILTERED_FEEDS = {
    "event_DelayMachine_PaymentCancel": ("source", "destination"),
    "event_DelayMachine_PaymentDeposit": ("source", "destination"),
    "event_DelayMachine_PaymentWithdraw": ("source", "destination"),
    "event_Supporters_AddStake": ("user", "subaccount", "sender"),
    "event_Supporters_Withdraw": ("msgSender", "subaccount", "receiver"),
    "event_Supporters_WithdrawStake": ("user", "subaccount", "destination"),
}
_INDEX_SPECS += [
    (collection, [(field, 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION})
    for collection, fields in _ADDRESS_FILTERED_FEEDS.items()
    for field in fields
]

# Several VotingMachine feeds can also be filtered by proposal address.
_INDEX_SPECS += [
    (collection, [("proposal", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION})
    for collection in (
        "event_VotingMachine_VoteEvent",
        "event_VotingMachine_PreVoteStepEvent",
        "event_VotingMachine_AcceptedStepEvent",
        "event_VotingMachine_UnregisterEvent",
    )
]

# The OracleManager feeds can be filtered by caller address.
_INDEX_SPECS += [
    (collection, [("caller", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION})
    for collection in (
        "event_OracleManager_OracleRegistered",
        "event_OracleManager_OracleStakeAdded",
        "event_OracleManager_OracleSubscribed",
        "event_OracleManager_OracleUnsubscribed",
        "event_OracleManager_OracleRemoved",
    )
]

# The CoinPairPrice feeds can be filtered by the coin pair's contract address.
_INDEX_SPECS += [
    (collection, [("contractAddress", 1), ("createdAt", -1)],
     {"collation": CASE_INSENSITIVE_COLLATION})
    for collection in (
        "event_CoinPairPrice_PricePublished",
        "event_CoinPairPrice_EmergencyPricePublished",
        "event_CoinPairPrice_ForcedPriceQueryModeSet",
        "event_CoinPairPrice_OracleRewardTransfer",
        "event_CoinPairPrice_NewRound",
        "event_CoinPairPrice_OracleAutoUnsubscribed",
    )
]

# The remaining OMoC event collections are served as unfiltered feeds sorted
# by createdAt desc (api/routers/omoc.py), so a plain createdAt index keeps
# the sort from blowing the in-memory sort limit as the logs grow.
_INDEX_SPECS += [
    (collection, [("createdAt", -1)], {})
    for collection in (
        "event_DelayMachine_PaymentCancel",
        "event_DelayMachine_PaymentDeposit",
        "event_DelayMachine_PaymentWithdraw",
        "event_Supporters_AddStake",
        "event_Supporters_CancelEarnings",
        "event_Supporters_PayEarnings",
        "event_Supporters_Withdraw",
        "event_Supporters_WithdrawStake",
        "event_VotingMachine_PreVoteEvent",
        "event_VotingMachine_VoteEvent",
        "event_VotingMachine_PreVoteStepEvent",
        "event_VotingMachine_VoteStepEvent",
        "event_VotingMachine_AcceptedStepEvent",
        "event_VotingMachine_UnregisterEvent",
        "event_OracleManager_OracleRegistered",
        "event_OracleManager_OracleStakeAdded",
        "event_OracleManager_OracleSubscribed",
        "event_OracleManager_OracleUnsubscribed",
        "event_OracleManager_OracleRemoved",
        "event_CoinPairPrice_PricePublished",
        "event_CoinPairPrice_EmergencyPricePublished",
        "event_CoinPairPrice_ForcedPriceQueryModeSet",
        "event_CoinPairPrice_OracleRewardTransfer",
        "event_CoinPairPrice_NewRound",
        "event_CoinPairPrice_OracleAutoUnsubscribed",
    )
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
    global db_client, _index_task
    uri = getenv("APP_MONGO_URI", default="mongodb://localhost:27017")
    try:
        db_client = AsyncIOMotorClient(uri)
        server_info = await db_client.server_info()
        log.info(f"Connected to mongo! (version {server_info['version']}).")
        # Scheduled, not awaited: a first-time index build on a large
        # existing collection can take far longer than the container
        # healthcheck's startup grace period, which would otherwise get
        # the (otherwise healthy) container killed before it ever serves
        # /ping. ensure_indexes() already catches and logs its own errors.
        _index_task = asyncio.create_task(ensure_indexes())
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

