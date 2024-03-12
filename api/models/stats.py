from datetime import date as date_type
from pydantic import BaseModel, computed_field
from typing import List, Optional
from enum import Enum


class Periods(Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

class TransactionsCountType(Enum):
    ALL = 'all'
    ONLY_NEW_ACCOUNTS = 'only_new_accounts'

class TransactionsCountFnc(str, Enum):
    COUNT = 'count'
    SUM = 'sum'

class TransactionsCountEvent(Enum):
    ALL = 'all'
    ONLY_TRANSFER = 'only_transfer'
    ONLY_MINT = 'only_mint'
    ONLY_REDEEM = 'only_redeem'
    ONLY_MINT_AND_REDEEM = 'only_mint_and_redeem'

class TransactionsCountToken(Enum):
    ALL = 'all'
    ONLY_STABLE = 'only_stable'
    ONLY_PRO = 'only_pro'
    ONLY_GOVERNANCE = 'only_governance'

class CountByDate(BaseModel):
    date: date_type
    count: float

    class Config:
        json_schema_extra = {
            "example": {
                "date": "1979-08-09",
                "count": 460.0
            }
        }


class TransactionsCountList(BaseModel):
    accounts: List[CountByDate]
    group_by: Optional[str] = None
    type: Optional[str] = None

    @computed_field
    @property
    def since(self) -> date_type:
        if not self.accounts:
            return None       
        return self.accounts[0].date

    @computed_field
    @property
    def to(self) -> date_type:
        if not self.accounts:
            return None
        return self.accounts[-1].date

    @computed_field
    @property
    def total(self) -> float:
        if not self.accounts:
            return 0.0
        return float(sum([a.count for a in self.accounts]))

    @computed_field
    @property
    def count(self) -> float:
        return float(len(self.accounts))

    class Config:
        json_schema_extra = {
            "example": {
                "accounts": [],
                "since": "1979-08-09",
                "to": "2009-01-03",
                "total": 32220,
                "count": 10740,
                "group_by": "day",
                "type": "all"
            }
        }
