from fastapi import APIRouter 
from api.db import db
from api.models.stats import TransactionsCountList, Periods, TransactionsCountType



link_url = 'https://grafana.moneyonchain.com/'
link_desc = "MOC's Grafana"
tags_metadata = [{
    "name": "Stats",
    "description": f"Used from apps like [{link_desc}]({link_url})"}]



router = APIRouter(tags=["Stats"])


@router.get(
    "/api/v1/stats/transactions/count",
    response_description="Successful Response",
    response_model = TransactionsCountList,
)
async def transactions_count(
    type: TransactionsCountType = TransactionsCountType.ONLY_NEW_ACCOUNTS,
    group_by: Periods = Periods.DAY,
    ):
    """
    Returns a list of the amount (per _day_, _week_, _month_ or _year_) of
    transactions that the protocol has had.
    """

    date_filter_per_week = {
        '$project': {
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
    }

    date_filter_per_month = {
        '$project': {
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
    }

    date_filter_per_day = {
        '$project': {
            'date': {
                '$dateToString': {
                    'format': '%Y-%m-%d', 
                    'date': '$timestamp'
                }
            }
        }
    }

    date_filter_per_year = {
        '$project': {
            'date': {
                '$dateToString': {
                    'format': '%Y-12-31', 
                    'date': '$timestamp'
                }
            }
        }
    }

    date_filter = date_filter_per_day
    if group_by==Periods.WEEK:
        date_filter = date_filter_per_week
    if group_by==Periods.MONTH:
        date_filter = date_filter_per_month
    if group_by==Periods.YEAR:
        date_filter = date_filter_per_year

    start_from_only_new_accounts = {
            '$group': {
                '_id': '$address', 
                'timestamp': {
                    '$first': '$confirmationTime'
                }
            }
        }

    start_from_all = {
            '$project': {
                'timestamp': '$confirmationTime'
            }
        }
    
    start_from = start_from_only_new_accounts
    if type==TransactionsCountType.ALL:
        start_from = start_from_all

    cursor = db["Transaction"].aggregate([
        start_from, {
            '$match': {
                'timestamp': {
                    '$ne': None
                }
            }    
        },
        date_filter,
        {
            '$group': {
                '_id': '$date', 
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }
    ])
 
    accounts = await cursor.to_list(length=None)
    transform_fnc = lambda x: {'date': x['_id'], 'count': x['count']}   
    accounts = [transform_fnc(a) for a in accounts]

    dict_values = {
        "accounts": accounts,
        "group_by": group_by.value,
        "type": type.value
    }

    return dict_values
