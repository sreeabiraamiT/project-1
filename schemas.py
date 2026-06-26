from pydantic import BaseModel, ConfigDict,Field
from datetime import date, datetime
from typing import List

class BillOut(BaseModel):
    id: int
    consumer_number: str
    region:str
    bill_month: date
    tariff_category: str
    units_consumed: float
    amount_due: float

    model_config = ConfigDict(from_attributes=True)

class AnalysisOut(BaseModel):
    id: int
    bill_id: int
    ai_summary: str
    saving_tips: List[str]

    model_config = ConfigDict(from_attributes=True)

class UploadBillResponse(BaseModel):
    consumer_number: str
    tariff_category: str
    region:str
    units_consumed: float
    amount_due: float
    bill_month: str
    ai_summary: str
    saving_tips: List[str]

    model_config = ConfigDict(from_attributes=True)


class TipsResponse(BaseModel):
    consumer_number: str
    saving_tips: List[str]


class HistoryItem(BaseModel):
    month: str
    units: float
    amount: float


class UserOut(BaseModel):
    consumer_number:str
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BillCreate(BaseModel):
    consumer_number: str=Field(...,min_length=10,max_length=12)
    bill_month: date
    tariff_category: str
    units_consumed: float
