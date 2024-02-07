from fastapi import APIRouter, Query, HTTPException
from typing import Annotated

from api.db import get_db
from api.models.fastbtc import mongo_date_to_str, PegOutList

from .common import make_responses


router = APIRouter()


@router.get(
    "/api/v1/webapp/fastbtc/pegout/",
    tags=["Webapp"],
    response_description="Successful Response",
    response_model=PegOutList,
    responses = make_responses(503)
)
async def peg_out_list(
        address: Annotated[str, Query(
            title="Address",
            description="User Address",
            regex='^0x[a-fA-F0-9]{40}$')] = '0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3',
        limit: Annotated[int, Query(
            title="Limit",
            description="Limit",
            le=1000)] = 20,
        skip: Annotated[int, Query(
            title="Skip",
            description="Skip",
            le=10000)] = 0):
    """
    Returns the pegout requests from an address
    """

    # get mongo db connection
    db = await get_db()

    if db is None:
        raise HTTPException(status_code=503, detail="Cannot get DB access")

    query_filter = {
        "rskAddress": {"$regex": address, '$options': 'i'},
        "type": "PEG_OUT"
    }

    transactions = await db["FastBtcBridge"]\
        .find(query_filter)\
        .sort("timestamp", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(limit)

    transactions_count = await db["FastBtcBridge"].count_documents(query_filter)

    for trx in transactions:
        trx['_id'] = str(trx['_id'])

        if trx.get("timestamp"):
            trx['timestamp'] = mongo_date_to_str(trx['timestamp'])

        if trx.get("updated"):
            trx['updated'] = mongo_date_to_str(trx['updated'])

    dict_values = {
        "pegout_requests": transactions,
        "count": len(transactions),
        "total": transactions_count
    }

    return dict_values
