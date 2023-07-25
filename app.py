from fastapi import FastAPI, Body, HTTPException, status, Query
from typing import Optional, List
from typing import Annotated

from db import db
from models import Transactions, TokenName, EXCLUDED_EVENTS

app = FastAPI()


@app.get(
    "/api/v1/webapp/transactions/list/",
    response_description="List operations of the given address user",
    response_model=List[Transactions]
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

    transactions = await db["Transaction"].find().to_list(1000)
    print(transactions)
    return transactions

