from fastapi import APIRouter 
from api.db import db
from api.models.stats import AccountsList
#from datetime import datetime, timezone



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
async def new_accounts_per_day():
    """
    Returns a list of the amount per day of new accounts
    that have interacted with the protocol.
    """

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
        #}, {
        #    '$match': {
        #        'firstSeen': {
        #            '$gte': datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 
        #            '$lt': datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        #        }
        #    }
        }, {
            '$project': {
                'date': {
                    '$dateToString': {
                        'format': '%Y-%m-%d', 
                        'date': '$firstSeen'
                    }
                }
            }
        }, {
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
    }

    return dict_values
