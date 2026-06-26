from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import TipsResponse

router = APIRouter()

@router.get("/tips/{consumer_number}", response_model=TipsResponse)
def get_saving_tips(consumer_number: str, db: Session = Depends(get_db)):
    
    # Query the latest bill matching the consumer_number
    latest_bill = db.query(models.Bill).filter(
        models.Bill.consumer_number == consumer_number
    ).order_by(models.Bill.bill_month.desc()).first()
    
    if not latest_bill:
        raise HTTPException(status_code=404, detail="No electricity bills found for this consumer number.")
        
    analysis = db.query(models.Analysis).filter(
        models.Analysis.bill_id == latest_bill.id
    ).first()
    
    if not analysis:
        return TipsResponse(
            consumer_number=consumer_number,
            saving_tips=["Tips pending AI analysis configuration. Make sure Gemini integration is active."]
        )
        
    return TipsResponse(
        consumer_number=consumer_number,
        saving_tips=analysis.saving_tips
    )
