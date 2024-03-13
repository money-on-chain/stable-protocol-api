import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import uuid


class TokenName(Enum):
    STABLE = 'STABLE'
    RISKPRO = 'RISKPRO'
    RISKPROX = 'RISKPROX'


class OutputFormat(Enum):
    JSON = 'json'
    TEXT = 'text'


EXCLUDED_EVENTS = [
    "RedeemRequestAlter",
    "RedeemRequestProcessed",
    "SettlementRedeemStableToken",
    "TransferFromMoC",
    "QueueDOC"
]


def mongo_date_to_str(x):
    return str(x.isoformat(timespec='milliseconds'))+"Z"


class Transactions(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    address: Optional[str]
    transactionHash: Optional[str]
    blockNumber: Optional[int] = None
    event: Optional[str] = None
    gas: Optional[int] = None
    gasPrice: Optional[str] = None
    gasUsed: Optional[int] = None
    gasFeeRBTC: Optional[str] = None
    RBTCAmount: Optional[str] = None
    RBTCTotal: Optional[str] = None
    USDAmount: Optional[str] = None
    USDCommission: Optional[str] = None
    USDInterests: Optional[str] = None
    USDTotal: Optional[str] = None
    amount: Optional[str] = None
    confirmationTime: Optional[datetime.datetime] = None
    createdAt: Optional[datetime.datetime] = None
    isPositive: Optional[bool] = None
    lastUpdatedAt: Optional[datetime.datetime] = None
    mocCommissionValue: Optional[str] = None
    mocPrice: Optional[str] = None
    processLogs: Optional[bool] = None
    rbtcCommission: Optional[str] = None
    rbtcInterests: Optional[str] = None
    reservePrice: Optional[str] = None
    status: Optional[str] = None
    tokenInvolved: Optional[str] = None
    userAmount: Optional[str] = None
    confirmingPercent: Optional[int] = None
    otherAddress: Optional[str] = None

    class Config:
        #allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "address": "0x0000000",
                "event": "TEST"
            }
        }


class TransactionsList(BaseModel):
    transactions: List[Transactions]
    count: int = 0
    total: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "transactions": "[]",
                "count": "0",
                "total": "0"
            }
        }
