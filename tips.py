from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import TipsResponse

router = APIRouter()

@router.get("/tips/{user_id}", response_model=TipsResponse)
def get_saving_tips(user_id: int, db: Session = Depends(get_db)):

    # Find the most recent AI-generated analysis for this user
    analysis = (
        db.query(models.Analysis)
        .join(models.Bill, models.Analysis.bill_id == models.Bill.id)
        .filter(models.Bill.user_id == user_id)
        .filter(
            models.Analysis.ai_summary !=
            "Manual Entry — insufficient data for AI analysis."
        )
        .order_by(models.Analysis.analyzed_at.desc())
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No AI-generated tips found for this user."
        )

    return TipsResponse(
        user_id=user_id,
        saving_tips=analysis.saving_tips
    )
