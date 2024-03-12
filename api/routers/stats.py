from fastapi import APIRouter, HTTPException
from api.db import get_db
from .common import make_responses
from api.models.stats import (TransactionsCountList, Periods,
                              TransactionsCountType, TransactionsCountToken,
                              TransactionsCountEvent, TransactionsCountFnc)


link_url = 'https://grafana.moneyonchain.com/'
link_desc = "MOC's Grafana"
tags_metadata = [{
    "name": "Stats",
    "description": f"Used from apps like [{link_desc}]({link_url})"}]


router = APIRouter(tags=["Stats"])


async def transactions_base(
    type: TransactionsCountType = TransactionsCountType.ONLY_NEW_ACCOUNTS,
    token: TransactionsCountToken = TransactionsCountToken.ALL,
    event: TransactionsCountEvent = TransactionsCountEvent.ALL,
    group_by: Periods = Periods.DAY,
    fnc: TransactionsCountFnc = TransactionsCountFnc.COUNT
    ):

    # get mongo db connection
    db = await get_db()

    if db is None:
        raise HTTPException(status_code=503, detail="Cannot get DB access")

    if type==TransactionsCountType.ONLY_NEW_ACCOUNTS \
            and fnc==TransactionsCountFnc.SUM:
        raise HTTPException(status_code=400,
            detail=(f"type={repr(type.value)} and fnc={repr(fnc.value)} " +
                    "does not make sense."))

    if token==TransactionsCountToken.ALL and fnc==TransactionsCountFnc.SUM:
        raise HTTPException(status_code=400,
            detail=(f"token={repr(token.value)} and fnc={repr(fnc.value)} " +
                    "does not make sense, it is mixing pears with apples."))

    if (token==TransactionsCountToken.ONLY_GOVERNANCE and
        event in [TransactionsCountEvent.ONLY_MINT,
                   TransactionsCountEvent.ONLY_REDEEM,
                   TransactionsCountEvent.ONLY_MINT_AND_REDEEM]):
        raise HTTPException(status_code=404,
            detail=("governance token cannot be redeemed or minted."))   

    query = []

    if token==TransactionsCountToken.ONLY_STABLE:
        query.append({
            '$match': {
                'tokenInvolved': 'STABLE'
            }    
        })
    elif token==TransactionsCountToken.ONLY_PRO:
        query.append({
            '$match': {
                'tokenInvolved': 'RISKPRO'
            }    
        })
    elif token==TransactionsCountToken.ONLY_GOVERNANCE:
        query.append({
            '$match': {
                'tokenInvolved': 'MOC'
            }    
        })

    if event==TransactionsCountEvent.ONLY_TRANSFER:
        query.append({
            '$match': {
                'event': 'Transfer'
            }    
        })
    elif event==TransactionsCountEvent.ONLY_MINT:
        query.append({
            '$match': {
                '$or': [
                    {'event' : "RiskProMint"},
                    {'event' : "StableTokenMint"}
                ]
            }    
        })
    elif event==TransactionsCountEvent.ONLY_REDEEM:
        query.append({
            '$match': {
                '$or': [
                    {'event' : "RiskProRedeem"},
                    {'event' : "FreeStableTokenRedeem"}
                ]
            }    
        })
    elif event==TransactionsCountEvent.ONLY_MINT_AND_REDEEM:
        query.append({
            '$match': {
                '$or': [
                    {'event' : "RiskProMint"},
                    {'event' : "StableTokenMint"},
                    {'event' : "RiskProRedeem"},
                    {'event' : "FreeStableTokenRedeem"}
                ]
            }    
        })

    if type==TransactionsCountType.ALL: # start from all
        query.append({
            '$project': {
                'amount': '$amount',
                'timestamp': '$confirmationTime'
            }
        })
    else: # start from only new accounts
        query.append({
            '$group': {
                '_id': '$address', 
                'timestamp': {
                    '$first': '$confirmationTime'
                }
            }
        })
    
    query.append({
        '$match': {
            'timestamp': {
                '$ne': None
            }
        }    
    })

    if group_by==Periods.WEEK:
        query.append({
            '$project': {
                'amount': '$amount',
                'date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': {
                            '$dateFromParts': {
                                'isoWeekYear': {
                                    '$year': '$timestamp'
                                }, 
                                'isoWeek': {
                                    '$isoWeek': '$timestamp'
                                },
                                "isoDayOfWeek": 7,
                            }
                        }
                    }
                }
            }
        })
    
    elif group_by==Periods.MONTH:
        query.append({
            '$project': {
                'amount': '$amount',
                'date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': {
                            '$subtract': [
                                {
                                    '$dateFromParts': {
                                        'year': {
                                            '$year': '$timestamp'
                                        }, 
                                        'month': {
                                            '$add': [
                                                {
                                                    '$month': '$timestamp'
                                                },
                                                1
                                            ]
                                        }
                                    }
                                },
                                86400000
                            ]
                        }
                    }
                }
            }
        })
    
    elif group_by==Periods.YEAR:
        query.append({
            '$project': {
                'amount': '$amount',
                'date': {
                    '$dateToString': {
                        'format': '%Y-12-31', 
                        'date': '$timestamp'
                    }
                }
            }
        })
    
    else: # group per day
        query.append({
            '$project': {
                'amount': '$amount',
                'date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$timestamp'
                    }
                }
            }
        })
    
    if fnc==TransactionsCountFnc.COUNT:
        query.append({
            '$group': {
                '_id': '$date', 
                'count': {
                    '$sum': 1.0
                }
            }
        })
    else:
        query.append({
            '$group': {
                '_id': '$date', 
                'count': {
                    '$sum': { '$toDecimal': '$amount' }
                }
            }
        })
    
    query.append({
        '$sort': {
            '_id': 1
        }
    })
    
    cursor = db["Transaction"].aggregate(query)
 
    accounts = await cursor.to_list(length=None)

    if fnc==TransactionsCountFnc.COUNT:
        transform_count = lambda x: float(str(x))
    else:
        transform_count = lambda x: float(str(x))/(10**18)

    transform_fnc = lambda x: {'date': x['_id'],
                               'count': transform_count(x['count']) }

    accounts = [transform_fnc(a) for a in accounts]

    dict_values = {
        "accounts": accounts,
        "group_by": group_by.value,
        "type": type.value
    }

    return dict_values


@router.get(
    "/api/v1/stats/volumen/stable",
    response_description="Successful Response",
    response_model = TransactionsCountList,
    responses = make_responses(503, 400, 404))
async def volumen_stable_token(
    event: TransactionsCountEvent = TransactionsCountEvent.ALL,
    group_by: Periods = Periods.DAY,
    ):
    """
    Returns a list of the volumen of (per _day_, _week_, _month_ or _year_) of
    the **Stable** token.
    """
    return await transactions_base(
        type = TransactionsCountType.ALL,
        token = TransactionsCountToken.ONLY_STABLE,
        event = event,
        group_by = group_by,
        fnc = TransactionsCountFnc.SUM
    )


@router.get(
    "/api/v1/stats/volumen/pro",
    response_description="Successful Response",
    response_model = TransactionsCountList,
    responses = make_responses(503, 400, 404))
async def volumen_pro_token(
    event: TransactionsCountEvent = TransactionsCountEvent.ALL,
    group_by: Periods = Periods.DAY,
    ):
    """
    Returns a list of the volumen of (per _day_, _week_, _month_ or _year_) of
    the **Pro** token.
    """
    return await transactions_base(
        type = TransactionsCountType.ALL,
        token = TransactionsCountToken.ONLY_PRO,
        event = event,
        group_by = group_by,
        fnc = TransactionsCountFnc.SUM
    )


@router.get(
    "/api/v1/stats/volumen/governance",
    response_description="Successful Response",
    response_model = TransactionsCountList,
    responses = make_responses(503, 400, 404))
async def volumen_governance_token(
    event: TransactionsCountEvent = TransactionsCountEvent.ALL,
    group_by: Periods = Periods.DAY,
    ):
    """
    Returns a list of the volumen of (per _day_, _week_, _month_ or _year_) of
    the **Governance** token.
    """
    return await transactions_base(
        type = TransactionsCountType.ALL,
        token = TransactionsCountToken.ONLY_GOVERNANCE,
        event = event,
        group_by = group_by,
        fnc = TransactionsCountFnc.SUM
    )


@router.get(
    "/api/v1/stats/transactions/{fnc}",
    response_description="Successful Response",
    response_model = TransactionsCountList,
    responses = make_responses(503, 400, 404))
async def transactions_count(
    type: TransactionsCountType = TransactionsCountType.ONLY_NEW_ACCOUNTS,
    token: TransactionsCountToken = TransactionsCountToken.ALL,
    event: TransactionsCountEvent = 3758.ALL,
    group_by: Periods = Periods.DAY,
    fnc: TransactionsCountFnc = TransactionsCountFnc.COUNT
    ):
    """
    Returns a list of the amount (per _day_, _week_, _month_ or _year_) of
    transactions that the protocol has had.

    *On this one are based the previous endpoints.*
    """
    return await transactions_base(
        type = type,
        token = token,
        event = event,
        group_by = group_by,
        fnc = fnc
    )
