import os
import datetime
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List

from db import db


app = FastAPI()
#client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
#db = client['flipago']


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DocumentTransactions(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hash: str
    blockNumber: int
    gas: int
    gasPrice: str
    gasUsed: int
    active: Optional[bool] = None
    reverted: Optional[bool] = None
    confirmations: int
    timestamp: datetime.datetime
    eventName: str
    sender_: Optional[str] = None
    recipient_: Optional[str] = None
    qTC_: Optional[str] = None
    qAC_: Optional[str] = None
    qACfee_: Optional[str] = None
    i_: Optional[int] = None
    qTP_: Optional[str] = None
    iFrom_: Optional[int] = None
    iTo_: Optional[int] = None
    qTPfrom_: Optional[str] = None
    qTPto_: Optional[str] = None
    from_: Optional[str] = None
    to_: Optional[str] = None
    value_: Optional[str] = None
    createdAt: datetime.datetime = Field(default=datetime.datetime.now())
    lastUpdatedAt: datetime.datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }


@app.get(
    "/", response_description="List all students", response_model=List[DocumentTransactions]
)
async def list_students():
    students = await db["transactions"].find().to_list(1000)
    print(students)
    return students


@app.get(
    "/{id}", response_description="Get a single student", response_model=DocumentTransactions
)
async def show_student(id: str):
    if (student := await db["transactions"].find_one({"_id": id})) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
