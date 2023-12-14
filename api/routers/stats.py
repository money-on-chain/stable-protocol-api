from fastapi import APIRouter 
from api.db import db
from api.models.stats import AccountsList
#from datetime import datetime, timezone


router = APIRouter()


@router.get(
    "/api/v1/stats/new-accounts/",
    tags=["stats"],
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
    filter_fnc = lambda x: x['_id'] is not None
    transform_fnc = lambda x: {'date': x['_id'], 'count': x['count']}   
    accounts = [transform_fnc(a) for a in filter(filter_fnc, accounts)]

    dict_values = {
        "accounts": accounts,
    }

    return dict_values
