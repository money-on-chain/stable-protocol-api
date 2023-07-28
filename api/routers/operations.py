from fastapi import APIRouter, Query
from typing import Annotated

from api.db import db
from api.models.operations import TokenName, EXCLUDED_EVENTS, mongo_date_to_str, TransactionsList


router = APIRouter()


@router.get(
    "/api/v1/webapp/transactions/list/",
    tags=["operations"],
    response_description="List operations of the given address user",
    response_model=TransactionsList
)
async def transactions_list(
        address: Annotated[str, Query(
            title="Address",
            description="User Address",
            regex='^0x[a-fA-F0-9]{40}$')] = '0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3',
        token: TokenName = None,
        limit: Annotated[int, Query(
            title="Limit",
            description="Limit",
            le=1000)] = 100,
        skip: Annotated[int, Query(
            title="Skip",
            description="Skip",
            le=10000)] = 0):

    query_filter = {
        "address": {"$regex": address, '$options': 'i'},
        "event": {"$not": {"$in": EXCLUDED_EVENTS}}
    }

    if token is not None:
        query_filter["tokenInvolved"] = token.value

    transactions = await db["Transaction"]\
        .find(query_filter)\
        .sort("createdAt", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(limit)

    transactions_count = await db["Transaction"].count_documents(query_filter)

    for trx in transactions:
        trx['_id'] = str(trx['_id'])

        if trx.get("createdAt"):
            trx['createdAt'] = mongo_date_to_str(trx['createdAt'])

        if trx.get("lastUpdatedAt"):
            trx['lastUpdatedAt'] = mongo_date_to_str(trx['lastUpdatedAt'])

        if trx.get("confirmationTime"):
            trx['confirmationTime'] = mongo_date_to_str(trx['confirmationTime'])

    dict_values = {
        "transactions": transactions,
        "count": len(transactions),
        "total": transactions_count
    }

    return dict_values
