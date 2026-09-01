import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

DATE_FIELDS = [
    'createdAt',
    'lastUpdatedAt',
]


def mongo_date_to_str(x):
    if not x:
        return None
    return str(x.isoformat(timespec='milliseconds')) + "Z"


def fields_date_to_str(fields, fields_date):

    for field_date in fields_date:
        v_date = field_date.split('.')
        if len(v_date) > 1:
            try:
                fields[v_date[0]][v_date[1]] = mongo_date_to_str(fields[v_date[0]][v_date[1]])
            except KeyError:
                pass
        else:
            try:
                fields[field_date] = mongo_date_to_str(fields[field_date])
            except KeyError:
                pass

    return fields


class VestingCreated(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    holder: Optional[str] = None
    vesting: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "holder": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "vesting": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "createdAt": None,
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VestingCreatedList(BaseModel):
    transactions: List[VestingCreated]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class ClaimOK(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    recipient: Optional[str] = None
    origin: Optional[str] = None
    value: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "recipient": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "origin": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "value": "177577695063561323",
                "createdAt": None,
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class ClaimOKList(BaseModel):
    results: List[ClaimOK]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class DelayMachinePaymentCancel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    idTx: int = Field(alias="id")
    source: Optional[str] = None
    destination: Optional[str] = None
    amount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "idTx": 15,
                "source": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "destination": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "amount": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class DelayMachinePaymentCancelList(BaseModel):
    results: List[DelayMachinePaymentCancel]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class DelayMachinePaymentDeposit(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    idTx: int = Field(alias="id")
    source: Optional[str] = None
    destination: Optional[str] = None
    amount: Optional[str] = None
    expiration: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "idTx": 15,
                "source": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "destination": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "amount": "177577695063561323",
                "expiration": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class DelayMachinePaymentDepositList(BaseModel):
    results: List[DelayMachinePaymentDeposit]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class DelayMachinePaymentWithdraw(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    idTx: int = Field(alias="id")
    source: Optional[str] = None
    destination: Optional[str] = None
    amount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "idTx": 15,
                "source": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "destination": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "amount": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class DelayMachinePaymentWithdrawList(BaseModel):
    results: List[DelayMachinePaymentWithdraw]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class SupportersAddStake(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    subaccount: Optional[str] = None
    sender: Optional[str] = None
    amount: Optional[str] = None
    mocs: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "user": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "subaccount": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "sender": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "amount": "177577695063561323",
                "mocs": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class SupportersAddStakeList(BaseModel):
    results: List[SupportersAddStake]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class SupportersCancelEarnings(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    earnings: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "earnings": "177577695063561323",
                "start": "177577695063561323",
                "end": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class SupportersCancelEarningsList(BaseModel):
    results: List[SupportersCancelEarnings]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class SupportersPayEarnings(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    earnings: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "earnings": "177577695063561323",
                "start": "177577695063561323",
                "end": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class SupportersPayEarningsList(BaseModel):
    results: List[SupportersPayEarnings]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class SupportersWithdraw(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    msgSender: Optional[str] = None
    subaccount: Optional[str] = None
    receiver: Optional[str] = None
    mocs: Optional[str] = None
    blockNum: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "msgSender": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "subaccount": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "receiver": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "mocs": "177577695063561323",
                "blockNum": 4643915,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class SupportersWithdrawList(BaseModel):
    results: List[SupportersWithdraw]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class SupportersWithdrawStake(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    subaccount: Optional[str] = None
    destination: Optional[str] = None
    amount: Optional[str] = None
    mocs: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "user": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "subaccount": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "destination": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "amount": "177577695063561323",
                "mocs": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class SupportersWithdrawStakeList(BaseModel):
    results: List[SupportersWithdrawStake]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachineVoteEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    proposal: Optional[str] = None
    inFavorAgainst: Optional[bool] = None
    stake: Optional[str] = None
    round: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "user": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "inFavorAgainst": True,
                "stake": "177577695063561323",
                "round": 3,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachineVoteEventList(BaseModel):
    results: List[VotingMachineVoteEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachinePreVoteEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    user: Optional[str] = None
    proposal: Optional[str] = None
    stake: Optional[str] = None
    round: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "user": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "stake": "177577695063561323",
                "round": 3,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachinePreVoteEventList(BaseModel):
    results: List[VotingMachinePreVoteEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachinePreVoteStepEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    proposal: Optional[str] = None
    votesInFavor: Optional[str] = None
    round: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "votesInFavor": "177577695063561323",
                "round": 3,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachinePreVoteStepEventList(BaseModel):
    results: List[VotingMachinePreVoteStepEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachineVoteStepEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    proposal: Optional[str] = None
    round: Optional[int] = None
    result: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "round": 3,
                "result": 1,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachineVoteStepEventList(BaseModel):
    results: List[VotingMachineVoteStepEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachineAcceptedStepEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    proposal: Optional[str] = None
    round: Optional[int] = None
    success: Optional[bool] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "round": 3,
                "success": True,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachineAcceptedStepEventList(BaseModel):
    results: List[VotingMachineAcceptedStepEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class VotingMachineUnregisterEvent(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    proposal: Optional[str] = None
    round: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "proposal": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "round": 3,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class VotingMachineUnregisterEventList(BaseModel):
    results: List[VotingMachineUnregisterEvent]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class OracleManagerOracleRegistered(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    caller: Optional[str] = None
    addr: Optional[str] = None
    internetName: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "addr": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "internetName": "https://oracle.example.com",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class OracleManagerOracleRegisteredList(BaseModel):
    results: List[OracleManagerOracleRegistered]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class OracleManagerOracleStakeAdded(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    caller: Optional[str] = None
    addr: Optional[str] = None
    stake: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "addr": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "stake": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class OracleManagerOracleStakeAddedList(BaseModel):
    results: List[OracleManagerOracleStakeAdded]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class OracleManagerOracleSubscribed(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    caller: Optional[str] = None
    coinpair: Optional[str] = None
    coinPairName: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "coinpair": "0x4254435553440000000000000000000000000000000000000000000000000000",
                "coinPairName": "BTCUSD",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class OracleManagerOracleSubscribedList(BaseModel):
    results: List[OracleManagerOracleSubscribed]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class OracleManagerOracleUnsubscribed(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    caller: Optional[str] = None
    coinpair: Optional[str] = None
    coinPairName: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "coinpair": "0x4254435553440000000000000000000000000000000000000000000000000000",
                "coinPairName": "BTCUSD",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class OracleManagerOracleUnsubscribedList(BaseModel):
    results: List[OracleManagerOracleUnsubscribed]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class OracleManagerOracleRemoved(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    caller: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class OracleManagerOracleRemovedList(BaseModel):
    results: List[OracleManagerOracleRemoved]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPricePricePublished(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    sender: Optional[str] = None
    price: Optional[str] = None
    votedOracle: Optional[str] = None
    priceBlockNumber: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "sender": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "price": "63500000000000000000000",
                "votedOracle": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "priceBlockNumber": "4643915",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPricePricePublishedList(BaseModel):
    results: List[CoinPairPricePricePublished]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPriceEmergencyPricePublished(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    sender: Optional[str] = None
    price: Optional[str] = None
    votedOracle: Optional[str] = None
    priceBlockNumber: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "sender": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "price": "63500000000000000000000",
                "votedOracle": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "priceBlockNumber": "4643915",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPriceEmergencyPricePublishedList(BaseModel):
    results: List[CoinPairPriceEmergencyPricePublished]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPriceForcedPriceQueryModeSet(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    setter: Optional[str] = None
    mode: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "setter": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "mode": 1,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPriceForcedPriceQueryModeSetList(BaseModel):
    results: List[CoinPairPriceForcedPriceQueryModeSet]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPriceOracleRewardTransfer(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    roundNumber: Optional[int] = None
    oracleOwnerAddress: Optional[str] = None
    toOwnerAddress: Optional[str] = None
    amount: Optional[str] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "roundNumber": 42,
                "oracleOwnerAddress": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "toOwnerAddress": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "amount": "177577695063561323",
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPriceOracleRewardTransferList(BaseModel):
    results: List[CoinPairPriceOracleRewardTransfer]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPriceNewRound(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    caller: Optional[str] = None
    number: Optional[int] = None
    totalPoints: Optional[str] = None
    startBlock: Optional[int] = None
    lockPeriodTimestamp: Optional[int] = None
    selectedOracles: Optional[List[str]] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "caller": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "number": 42,
                "totalPoints": "1000",
                "startBlock": 4643900,
                "lockPeriodTimestamp": 1703772901,
                "selectedOracles": [
                    "0xcd8a1c9acc980ae031456573e34dc05cd7dae6e3"
                ],
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPriceNewRoundList(BaseModel):
    results: List[CoinPairPriceNewRound]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }


class CoinPairPriceOracleAutoUnsubscribed(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    hash: Optional[str] = None
    blockNumber: Optional[int] = None
    contractAddress: Optional[str] = None
    coinPair: Optional[str] = None
    oracleOwnerAddr: Optional[str] = None
    coinPairId: Optional[str] = None
    roundNumber: Optional[int] = None
    missedSignatureRounds: Optional[int] = None
    createdAt: Optional[datetime.datetime] = None
    lastUpdatedAt: Optional[datetime.datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "658dac848e6961287ceb62e5",
                "hash": "0xaddc1a3b49fcd5528a4a394d98e095c1f89475e1e30b9a237e93231c15e4a265",
                "blockNumber": 4643915,
                "contractAddress": "0xF20Ee80f56F41b6323D140b07A011c77509Fb99D",
                "coinPair": "BTCUSD",
                "oracleOwnerAddr": "0xCD8A1c9aCc980ae031456573e34dC05cD7daE6e3",
                "coinPairId": "0x4254435553440000000000000000000000000000000000000000000000000000",
                "roundNumber": 42,
                "missedSignatureRounds": 3,
                "createdAt": "2023-12-28T14:15:01.629000Z",
                "lastUpdatedAt": "2023-12-28T14:15:01.629000Z"
            }
        }


class CoinPairPriceOracleAutoUnsubscribedList(BaseModel):
    results: List[CoinPairPriceOracleAutoUnsubscribed]
    count: int = 0
    total: int = 0
    last_block_indexed: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "results": "[]",
                "count": "0",
                "total": "0",
                "last_block_indexed": "12345678"
            }
        }
