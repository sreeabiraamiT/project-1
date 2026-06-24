from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List

class BillOut(BaseModel):
    id: int
    user_id: int
    consumer_number: str
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
    bill_id: int
    tariff_category: str
    units_consumed: float
    amount_due: float
    bill_month: str
    ai_summary: str
    saving_tips: List[str]  # <-- Add this to match what the pipeline unifies!

    model_config = ConfigDict(from_attributes=True)


class TipsResponse(BaseModel):
    user_id: int
    saving_tips: List[str]


class HistoryItem(BaseModel):
    month: str
    units: float
    amount: float


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BillCreate(BaseModel):
    consumer_number: str
    bill_month: date
    tariff_category: str
    units_consumed: float