import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
import uuid


DATE_FIELDS = [
    'createdAt',
    'lastUpdatedAt',
]

EXAMPLE_HASH = "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265"
EXAMPLE_ID = "658dac848e6961287ceb62e5"
EXAMPLE_BLOCK = 4643915
EXAMPLE_USER = "0xcd8a1c9acc980ae031456573e34dc05cd7dae6e3"
EXAMPLE_TP_TOKEN = "0x0AE66294941fdA20c336cfC57EEAF5C2c35cecB4"
EXAMPLE_BUCKET = "0xA27024Ed70035E46dba712609fc2Afa1c97aA36A"
EXAMPLE_AMOUNT = "5000000000000000000"
EXAMPLE_UPDATED = "2023-12-28T14:15:01.629000Z"


# Deposit

class EventLendingDeposit(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    tpAmount: Optional[str] = None
    depositUnits: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:10",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "tpAmount": EXAMPLE_AMOUNT,
                "depositUnits": "4950000000000000000",
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingDepositList(BaseModel):
    rows: List[EventLendingDeposit]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# Withdraw

class EventLendingWithdraw(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    depositUnits: Optional[str] = None
    tpAmount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:11",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "depositUnits": "4950000000000000000",
                "tpAmount": EXAMPLE_AMOUNT,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingWithdrawList(BaseModel):
    rows: List[EventLendingWithdraw]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# AddACtoVault

class EventLendingAddACtoVault(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    acAmount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:12",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "acAmount": EXAMPLE_AMOUNT,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingAddACtoVaultList(BaseModel):
    rows: List[EventLendingAddACtoVault]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# RemoveACfromVault

class EventLendingRemoveACfromVault(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    acAmount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:13",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "acAmount": EXAMPLE_AMOUNT,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingRemoveACfromVaultList(BaseModel):
    rows: List[EventLendingRemoveACfromVault]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# Borrow

class EventLendingBorrow(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    tpAmount: Optional[str] = None
    creditUnits: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:14",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "tpAmount": EXAMPLE_AMOUNT,
                "creditUnits": "4900000000000000000",
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingBorrowList(BaseModel):
    rows: List[EventLendingBorrow]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# Repay

class EventLendingRepay(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    creditUnits: Optional[str] = None
    tpAmount: Optional[str] = None
    tpToFeeFlow: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:15",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "creditUnits": "4900000000000000000",
                "tpAmount": EXAMPLE_AMOUNT,
                "tpToFeeFlow": "50000000000000000",
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingRepayList(BaseModel):
    rows: List[EventLendingRepay]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# RepayWithAC

class EventLendingRepayWithAC(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    creditUnits: Optional[str] = None
    acSold: Optional[str] = None
    tpAmount: Optional[str] = None
    tpToFeeFlow: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:16",
                "blockNumber": EXAMPLE_BLOCK,
                "user": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "creditUnits": "4900000000000000000",
                "acSold": "5100000000000000000",
                "tpAmount": EXAMPLE_AMOUNT,
                "tpToFeeFlow": "50000000000000000",
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingRepayWithACList(BaseModel):
    rows: List[EventLendingRepayWithAC]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# Liquidate

class EventLendingLiquidate(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    liquidator: Optional[str] = None
    user: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    acSwapped: Optional[str] = None
    tpPaid: Optional[str] = None
    tpToFeeFlow: Optional[str] = None
    isComplete: Optional[bool] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:17",
                "blockNumber": EXAMPLE_BLOCK,
                "liquidator": EXAMPLE_USER,
                "user": "0xaabbccddeeff00112233445566778899aabbccdd",
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "acSwapped": EXAMPLE_AMOUNT,
                "tpPaid": EXAMPLE_AMOUNT,
                "tpToFeeFlow": "50000000000000000",
                "isComplete": True,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingLiquidateList(BaseModel):
    rows: List[EventLendingLiquidate]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# TPInjection

class EventLendingTPInjection(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    tpToken: Optional[str] = None
    tpAmount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:18",
                "blockNumber": EXAMPLE_BLOCK,
                "tpToken": EXAMPLE_TP_TOKEN,
                "tpAmount": EXAMPLE_AMOUNT,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingTPInjectionList(BaseModel):
    rows: List[EventLendingTPInjection]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# OperationQueued

class EventLendingOperationQueued(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    operId: Optional[int] = None
    operType: Optional[int] = None
    operTypeName: Optional[str] = None
    user: Optional[str] = None
    recipient: Optional[str] = None
    tpToken: Optional[str] = None
    mocBucket: Optional[str] = None
    amount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:19",
                "blockNumber": EXAMPLE_BLOCK,
                "operId": 42,
                "operType": 1,
                "operTypeName": "BORROW",
                "user": EXAMPLE_USER,
                "recipient": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "mocBucket": EXAMPLE_BUCKET,
                "amount": EXAMPLE_AMOUNT,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingOperationQueuedList(BaseModel):
    rows: List[EventLendingOperationQueued]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# OperationError

class EventLendingOperationError(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    operId: Optional[int] = None
    reason: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:20",
                "blockNumber": EXAMPLE_BLOCK,
                "operId": 42,
                "reason": "0x54cde313",
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingOperationErrorList(BaseModel):
    rows: List[EventLendingOperationError]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# OperationExecuted

class EventLendingOperationExecuted(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    id_event: Optional[str] = None
    blockNumber: Optional[int] = None
    executor: Optional[str] = None
    operId: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "hash": EXAMPLE_HASH,
                "id_event": f"{EXAMPLE_HASH}:21",
                "blockNumber": EXAMPLE_BLOCK,
                "executor": EXAMPLE_USER,
                "operId": 42,
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class EventLendingOperationExecutedList(BaseModel):
    rows: List[EventLendingOperationExecuted]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }


# LendingUserOperation — unified activity feed across all lending event types

class LendingUserOperation(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    id_event: Optional[str] = None
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    eventName: Optional[str] = None
    user: Optional[str] = None
    tpToken: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": EXAMPLE_ID,
                "id_event": f"{EXAMPLE_HASH}:14",
                "hash": EXAMPLE_HASH,
                "blockNumber": EXAMPLE_BLOCK,
                "eventName": "Borrow",
                "user": EXAMPLE_USER,
                "tpToken": EXAMPLE_TP_TOKEN,
                "extra": {
                    "recipient": EXAMPLE_USER,
                    "mocBucket": EXAMPLE_BUCKET,
                    "tpAmount": EXAMPLE_AMOUNT,
                    "creditUnits": "4900000000000000000"
                },
                "createdAt": None,
                "lastUpdatedAt": EXAMPLE_UPDATED
            }
        }


class LendingUserOperationList(BaseModel):
    rows: List[LendingUserOperation]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {"rows": "[]", "count": "0", "total": "0", "last_block_indexed": "12345678"}
        }
