import datetime
from pydantic import BaseModel
from typing import Optional, List


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
                  "transferId": "0x8aba91c068c9456e93b749b5fffae005056c6c0f80077b8a69a95c4ceed3df9a",
                  "amountSatoshi": "33361401",
                  "blockNumber": 5459694,
                  "btcAddress": "1MQAHsr3QrGvBJVsEy4RJFQKNoE6p8yhg1",
                  "feeSatoshi": "88299",
                  "nonce": 41,
                  "processLogs": "true",
                  "rskAddress": "0x83b603ac42B942fe607d76A51a0Ab65BDf3787e4",
                  "status": 0,
                  "timestamp": "2023-07-10T05:50:29Z",
                  "transactionHash": "0xdbb7f54d6c5b2c40c9673ef1de90f5360f1c8d4f1b2754202e8c67a224354b92",
                  "transactionHashLastUpdated": "0xdbb7f54d6c5b2c40c9673ef1de90f5360f1c8d4f1b2754202e8c67a224354b92",
                  "type": "PEG_OUT",
                  "updated": "2023-07-10T05:50:29Z"
            }
        }


class PegOutList(BaseModel):
    pegout_requests: List[FastBtcBridge]
    count: int = 0
    total: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "pegout_requests": "[]",
                "count": "0",
                "total": "0"
            }
        }
