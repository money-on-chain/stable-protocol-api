import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TokenName(Enum):
    STABLE = 'STABLE'
    RISKPRO = 'RISKPRO'
    RISKPROX = 'RISKPROX'


EXCLUDED_EVENTS = [
    "RedeemRequestAlter",
    "RedeemRequestProcessed",
    "SettlementRedeemStableToken",
    "TransferFromMoC",
    "QueueDOC"
]


def mongo_date_to_str(x):
    return str(x.isoformat(timespec='milliseconds'))+"Z"


class FastBtcBridge(BaseModel):
    transferId: str
    amountSatoshi: str
    blockNumber: int
    btcAddress: str
    feeSatoshi: str
    nonce: int
    processLogs: bool
    rskAddress: str
    status: int
    timestamp: datetime.datetime
    transactionHash: str
    transactionHashLastUpdated: Optional[str] = None
    type: str
    updated: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "address": "0x0000000",
                "event": "TEST"
            }
        }


class PegOutList(BaseModel):
    pegout_requests: List[FastBtcBridge]

    class Config:
        json_schema_extra = {
            "example": {
                "transactions": "[]",
                "count": "0",
                "total": "0"
            }
        }
