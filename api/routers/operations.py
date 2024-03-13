from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Annotated
from tabulate import tabulate
from decimal import Decimal

from api.db import get_db, VENDOR_ADDRESS, COMMISSION_SPLITTER_V2
from api.models.operations import TokenName, EXCLUDED_EVENTS, \
    mongo_date_to_str, TransactionsList

from api.models.common import OutputFormat

from .common import make_responses


router = APIRouter()


@router.get(
    "/api/v1/webapp/transactions/list/",
    tags=["Webapp"],
    response_description="Successful Response",
    response_model=TransactionsList,
    responses = make_responses(
       (200, {
           "description": "Successful Response",
           "content": {
                "text/plain": {
                   "example": """Account: 0x0000000000000000000000000000000000000001
======== ==========================================

Token:  All
Total:  123

Date / time            #Block  Asset       Event            Platform        Wallet  Destination or origin
-------------------  --------  ----------  --------  ---------------  ------------  ------------------------------------------
2024-02-08 14:35:27   6065900  Stable      Transfer    -549.78                      0x0000000000000000000000000000000000000002
2024-02-06 02:59:20   6058963  Stable      Transfer    1900                         0x0000000000000000000000000000000000000003
2023-06-07 19:49:06   5369967  Stable      Redeem      -200            0.00474603
...
2022-06-15 21:27:10   4395956  Pro         Mint           0.00564821  -0.00815878
2022-06-15 21:22:26   4395943  Stable      Redeem      -300            0.00916788
2022-06-06 12:26:54   4370917  Stable      Transfer    -600                         0x0000000000000000000000000000000000000004
"""
                },
                "application/json": {
                   "example": {
                         "count": "0",
                         "total": "0",
                         "transactions": "[]"
                   }
                }
            }
        }),
        503
    )
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
            le=1000)] = 20,
        skip: Annotated[int, Query(
            title="Skip",
            description="Skip",
            le=10000)] = 0,
        format: OutputFormat = None,
        ):
    """
    Returns a list of operations of the given address user
    """

    # get mongo db connection
    db = await get_db()

    if db is None:
        raise HTTPException(status_code=503, detail="Cannot get DB access")

    query_filter = {
        "address": {"$regex": address, '$options': 'i'},
        "event": {"$not": {"$in": EXCLUDED_EVENTS}},
        "otherAddress": {"$not": {"$in": [VENDOR_ADDRESS, COMMISSION_SPLITTER_V2]}}
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

    if format in [OutputFormat.JSON, None]:

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
    
    table = []
    
    for tx in transactions:
        
        row = []

        for key in ['createdAt', 'blockNumber']:
            row.append(tx.get(key, None))
        
        asset = str(tx['tokenInvolved'])       
        if asset==TokenName.RISKPRO.value:
            asset = 'Pro'
        elif asset==TokenName.RISKPROX.value:
            asset = 'ProX'
        elif asset==TokenName.STABLE.value:
            asset = 'Stable'
        else:
            asset = asset.lower()
        asset = {
            'tg': 'Governance'
        }.get(asset, asset)   
        row.append(asset)

        event = str(tx['event']).lower()
        if 'mint' in event:
            event = 'mint'
        elif 'redeem' in event:
            event = 'redeem'
        row.append(event.title())

        platform = Decimal(tx.get('amount', 0))/Decimal(10**18)
        if event=='redeem':
            platform = -platform
        elif event=='transfer' and not(tx['isPositive']):
            platform = -platform
        row.append(platform)

        wallet = tx.get('RBTCTotal', None)
        if wallet is not None:
            wallet = Decimal(wallet)/Decimal(10**18)
            if event!='redeem':
                wallet = -wallet
        row.append(wallet)

        row.append(tx.get('otherAddress', None))

        table.append(row)

    text = []

    title = f"Account: {address}"

    str_token = 'All'
    if token==TokenName.RISKPRO:
        str_token = 'Pro'
    elif token==TokenName.RISKPROX:
        str_token = 'ProX'
    elif token==TokenName.STABLE:
        str_token = 'Stable'

    title = ' '.join(title.split())
    text.append(title)       
    text.append(' '.join([len(x)*"=" for x in title.split()]))       
    text.append('')    
    if len(transactions)==transactions_count:
        text.append(tabulate([
            ['Token:', str_token],
            ['Total:', transactions_count]
        ], tablefmt='plain'))
    else:
        text.append(tabulate([
            ['Token:', str_token],
            ['Limit:', limit],
            ['Skip:', skip],
            ['Count:', len(transactions)],
            ['Total:', transactions_count]
        ], tablefmt='plain'))
    text.append('')
    text.append(tabulate(table,
                            headers=[
                                'Date / time', '#Block', 'Asset',
                                'Event', 'Platform', 'Wallet',
                                'Destination or origin']))
    text.append('')
    text = '\n'.join(text)

    response = PlainTextResponse(text)

    response.headers["Content-Disposition"] = f"attachment; filename=tx_account_{address}.txt"

    return response

