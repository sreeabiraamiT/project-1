from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import HistoryItem
from typing import List

router = APIRouter()

@router.get("/history/{consumer_number}", response_model=List[HistoryItem])
def get_bill_history(consumer_number: str, db: Session = Depends(get_db)):
   
    # Query directly by consumer_number string
    bills = db.query(models.Bill).filter(
        models.Bill.consumer_number == consumer_number
    ).order_by(models.Bill.bill_month.asc()).all()
    
    history_data = []
    for bill in bills:
        formatted_month = bill.bill_month.strftime("%b %Y") if hasattr(bill.bill_month, 'strftime') else str(bill.bill_month)
        
        history_data.append(
            HistoryItem(
                month=formatted_month,
                units=bill.units_consumed,
                amount=bill.amount_due
            )
        )
    if not history_data:
        raise HTTPException(status_code=404, detail="No bill history found for this consumer number")
    return history_data
