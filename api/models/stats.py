from datetime import date as date_type
from pydantic import BaseModel, computed_field
from typing import List, Optional
from enum import Enum


class Periods(Enum):
    DAY = 'day'
    WEEK = 'week'



class CountByDate(BaseModel):
    date: date_type
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "date": "1979-08-09",
                "count": 46
            }
        }


class AccountsList(BaseModel):
    accounts: List[CountByDate]
    group_by: Optional[str] = None

    @computed_field
    @property
    def since(self) -> date_type:       
        return self.accounts[0].date

    @computed_field
    @property
    def to(self) -> date_type:
        return self.accounts[-1].date

    @computed_field
    @property
    def total(self) -> int:
        return sum([a.count for a in self.accounts])

    @computed_field
    @property
    def count(self) -> int:
        return len(self.accounts)

    class Config:
        json_schema_extra = {
            "example": {
                "accounts": "[]",
                "since": "1979-08-09",
                "to": "2009-10-03",
                "total": 456,
                "count": 123
            }
        }
