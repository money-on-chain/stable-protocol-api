from fastapi import APIRouter, Query, HTTPException
from typing import Annotated, Optional

from api.db import get_db
from api.models.lending import (
    EventLendingDepositList,
    EventLendingWithdrawList,
    EventLendingAddACtoVaultList,
    EventLendingRemoveACfromVaultList,
    EventLendingBorrowList,
    EventLendingRepayList,
    EventLendingRepayWithACList,
    EventLendingLiquidateList,
    EventLendingTPInjectionList,
    EventLendingOperationQueuedList,
    EventLendingOperationErrorList,
    EventLendingOperationExecutedList,
    LendingUserOperationList,
    DATE_FIELDS,
)
from api.utils import fields_date_to_str

EXAMPLE_ADDRESS = '0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3'
ADDRESS_PATTERN = '^0x[a-fA-F0-9]{40}$'

tags_metadata = [{
    "name": "Lending",
    "description": "Events and unified activity feed for the Lending protocol"}]

router = APIRouter(tags=["Lending"])


async def _get_last_block_indexed(db) -> int:
    indexer = await db["moc_indexer"].find_one(sort=[("updatedAt", -1)])
    if indexer and 'last_raw_tx_block' in indexer:
        return indexer['last_raw_tx_block']
    return 0


async def _query_collection(db, collection_name: str, query_filter: dict, limit: int, skip: int) -> dict:
    rows = await db[collection_name] \
        .find(query_filter) \
        .sort("blockNumber", -1) \
        .skip(skip) \
        .limit(limit) \
        .to_list(limit)

    rows_count = await db[collection_name].count_documents(query_filter)

    for row in rows:
        row['_id'] = str(row['_id'])
        fields_date_to_str(row, DATE_FIELDS)

    last_block_indexed = await _get_last_block_indexed(db)

    return {
        "rows": rows,
        "count": len(rows),
        "total": rows_count,
        "last_block_indexed": last_block_indexed
    }


@router.get(
    "/api/v1/lending/deposits/",
    response_description="Lending Deposit events",
    response_model=EventLendingDepositList
)
async def lending_deposits(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_Deposit", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/withdrawals/",
    response_description="Lending Withdraw events",
    response_model=EventLendingWithdrawList
)
async def lending_withdrawals(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_Withdraw", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/add_ac_to_vault/",
    response_description="Lending AddACtoVault events",
    response_model=EventLendingAddACtoVaultList
)
async def lending_add_ac_to_vault(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_AddACtoVault", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/remove_ac_from_vault/",
    response_description="Lending RemoveACfromVault events",
    response_model=EventLendingRemoveACfromVaultList
)
async def lending_remove_ac_from_vault(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_RemoveACfromVault", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/borrows/",
    response_description="Lending Borrow events",
    response_model=EventLendingBorrowList
)
async def lending_borrows(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_Borrow", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/repays/",
    response_description="Lending Repay events",
    response_model=EventLendingRepayList
)
async def lending_repays(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_Repay", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/repays_with_ac/",
    response_description="Lending RepayWithAC events",
    response_model=EventLendingRepayWithACList
)
async def lending_repays_with_ac(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        query_filter = {"user": user.lower()}

    return await _query_collection(db, "event_Lending_RepayWithAC", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/liquidations/",
    response_description="Lending Liquidate events",
    response_model=EventLendingLiquidateList
)
async def lending_liquidations(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by liquidated user or liquidator address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"liquidator": addr}]}

    return await _query_collection(db, "event_Lending_Liquidate", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/tp_injections/",
    response_description="Lending TPInjection events",
    response_model=EventLendingTPInjectionList
)
async def lending_tp_injections(
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    return await _query_collection(db, "event_Lending_TPInjection", {}, limit, skip)


@router.get(
    "/api/v1/lending/operation_queued/",
    response_description="Lending OperationQueued events",
    response_model=EventLendingOperationQueuedList
)
async def lending_operation_queued(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user or recipient address",
            pattern=ADDRESS_PATTERN)] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if user:
        addr = user.lower()
        query_filter = {"$or": [{"user": addr}, {"recipient": addr}]}

    return await _query_collection(db, "event_Lending_OperationQueued", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/operation_error/",
    response_description="Lending OperationError events",
    response_model=EventLendingOperationErrorList
)
async def lending_operation_error(
        oper_id: Annotated[Optional[int], Query(
            title="Operation ID",
            description="Filter by operation ID")] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if oper_id is not None:
        query_filter = {"operId": oper_id}

    return await _query_collection(db, "event_Lending_OperationError", query_filter, limit, skip)


@router.get(
    "/api/v1/lending/operation_executed/",
    response_description="Lending OperationExecuted events",
    response_model=EventLendingOperationExecutedList
)
async def lending_operation_executed(
        oper_id: Annotated[Optional[int], Query(
            title="Operation ID",
            description="Filter by operation ID")] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    query_filter = {}
    if oper_id is not None:
        query_filter = {"operId": oper_id}

    return await _query_collection(db, "event_Lending_OperationExecuted", query_filter, limit, skip)


VALID_EVENT_NAMES = {
    "Deposit", "Withdraw", "AddACtoVault", "RemoveACfromVault",
    "Borrow", "Repay", "RepayWithAC", "Liquidate"
}


@router.get(
    "/api/v1/lending/user_operations/",
    response_description="Unified lending activity feed for a user across all event types",
    response_model=LendingUserOperationList
)
async def lending_user_operations(
        user: Annotated[Optional[str], Query(
            title="User address",
            description="Filter by user address",
            pattern=ADDRESS_PATTERN)] = None,
        event_name: Annotated[Optional[str], Query(
            title="Event name",
            description="Filter by event type: Deposit, Withdraw, AddACtoVault, RemoveACfromVault, Borrow, Repay, RepayWithAC, Liquidate"
        )] = None,
        limit: Annotated[int, Query(title="Limit", description="Limit", le=1000)] = 20,
        skip: Annotated[int, Query(title="Skip", description="Skip", le=10000)] = 0
):
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=400, detail="Cannot get DB")

    if event_name is not None and event_name not in VALID_EVENT_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_name. Valid values: {', '.join(sorted(VALID_EVENT_NAMES))}"
        )

    query_filter = {}
    if user:
        query_filter["user"] = user.lower()
    if event_name:
        query_filter["eventName"] = event_name

    return await _query_collection(db, "lending_user_operations", query_filter, limit, skip)
