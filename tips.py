from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import TipsResponse

router = APIRouter()

@router.get("/tips/{user_id}", response_model=TipsResponse)
def get_saving_tips(user_id: int, db: Session = Depends(get_db)):
    
    latest_bill = db.query(models.Bill).filter(
        models.Bill.user_id == user_id
    ).order_by(models.Bill.bill_month.desc()).first()
    
    if not latest_bill:
        raise HTTPException(status_code=404, detail="No electricity bills found for this user.")
        
    
    analysis = db.query(models.Analysis).filter(
        models.Analysis.bill_id == latest_bill.id
    ).first()
    
    if not analysis:
        
            return TipsResponse(
            user_id=user_id,
            saving_tips=["Tips pending AI analysis configuration. Make sure Claude integration is active."]
        )
        
    return TipsResponse(
        user_id=user_id,
        saving_tips=analysis.saving_tips
    )