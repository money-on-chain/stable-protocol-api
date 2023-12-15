from fastapi import APIRouter 
from api.db import db
from api.models.stats import AccountsList, Periods



link_url = 'https://grafana.moneyonchain.com/'
link_desc = "MOC's Grafana"
tags_metadata = [{
    "name": "Stats",
    "description": f"Used from apps like [{link_desc}]({link_url})"}]



router = APIRouter(tags=["Stats"])


@router.get(
    "/api/v1/stats/new-accounts/",
    response_description="Successful Response",
    response_model = AccountsList,
)
async def new_accounts(group_by: Periods = Periods.DAY):
    """
    Returns a list of the amount per _day_, _week_, _month_ or _year_ of new
    accounts that have interacted with the protocol.
    """

    date_filter_per_week = {
        '$project': {
            'date': {
                '$dateToString': {
                    'format': '%Y-%m-%d', 
                    'date': {
                        '$dateFromParts': {
                            'isoWeekYear': {
                                '$year': '$firstSeen'
                            }, 
                            'isoWeek': {
                                '$isoWeek': '$firstSeen'
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
                                        '$year': '$firstSeen'
                                    }, 
                                    'month': {
                                        '$add': [
                                            {
                                                '$month': '$firstSeen'
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
                    'date': '$firstSeen'
                }
            }
        }
    }

    date_filter_per_year = {
        '$project': {
            'date': {
                '$dateToString': {
                    'format': '%Y-12-31', 
                    'date': '$firstSeen'
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

    cursor = db["Transaction"].aggregate([
        {
            '$group': {
                '_id': '$address', 
                'firstSeen': {
                    '$first': '$confirmationTime'
                }
            }
        }, {
            '$match': {
                'firstSeen': {
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
        "group_by": group_by.value
    }

    return dict_values
