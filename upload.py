from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import UploadBillResponse,CostBreakdown
from datetime import date
from typing import Optional

from services import (
    run_complete_student2_pipeline,
    generate_tips_for_manual_entry,
    AIServiceUnavailableError,
)

router = APIRouter()
REGION_MAP = {
    "01": "Chennai North",
    "02": "Chennai South",
    "03": "Coimbatore",
    "04": "Madurai",
    "05": "Thanjavur",
    "06": "Trichy",
    "07": "Salem",
    "08": "Tirunelveli",
    "09": "Vellore",
    "10": "Erode"
}

def calculate_amount_due(units_consumed: float, tariff_category: str):
    tariff = tariff_category.strip().lower()
    cost_breakdown=[]
    if tariff == "domestic":
        cost_breakdown = []

        if units_consumed <= 200:
            amount_due = 0

            cost_breakdown.append({
            "slab": "0-200",
            "units": units_consumed,
            "rate": 0,
            "cost": 0
        })

        elif units_consumed <= 400:
            slab2 = units_consumed - 200
            amount_due = slab2 * 4.70

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": slab2, "rate": 4.70, "cost": round(slab2 * 4.70, 2)}
        ]

        elif units_consumed <= 500:
            slab2 = 200
            slab3 = units_consumed - 400

            amount_due = (slab2 * 4.70) + (slab3 * 6.30)

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": 200, "rate": 4.70, "cost": 940},
            {"slab": "401-500", "units": slab3, "rate": 6.30, "cost": round(slab3 * 6.30, 2)}
        ]

        elif units_consumed <= 600:
            slab2 = 200
            slab3 = 100
            slab4 = units_consumed - 500

            amount_due = (slab2 * 4.70) + (slab3 * 6.30) + (slab4 * 8.40)

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": 200, "rate": 4.70, "cost": 940},
            {"slab": "401-500", "units": 100, "rate": 6.30, "cost": 630},
            {"slab": "501-600", "units": slab4, "rate": 8.40, "cost": round(slab4 * 8.40, 2)}
        ]

        elif units_consumed <= 800:
            slab2 = 200
            slab3 = 100
            slab4 = 100
            slab5 = units_consumed - 600

            amount_due = (
            (slab2 * 4.70)
            + (slab3 * 6.30)
            + (slab4 * 8.40)
            + (slab5 * 9.45)
        )

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": 200, "rate": 4.70, "cost": 940},
            {"slab": "401-500", "units": 100, "rate": 6.30, "cost": 630},
            {"slab": "501-600", "units": 100, "rate": 8.40, "cost": 840},
            {"slab": "601-800", "units": slab5, "rate": 9.45, "cost": round(slab5 * 9.45, 2)}
        ]

        elif units_consumed <= 1000:
            slab2 = 200
            slab3 = 100
            slab4 = 100
            slab5 = 200
            slab6 = units_consumed - 800

            amount_due = (
            (slab2 * 4.70)
            + (slab3 * 6.30)
            + (slab4 * 8.40)
            + (slab5 * 9.45)
            + (slab6 * 10.50)
        )

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": 200, "rate": 4.70, "cost": 940},
            {"slab": "401-500", "units": 100, "rate": 6.30, "cost": 630},
            {"slab": "501-600", "units": 100, "rate": 8.40, "cost": 840},
            {"slab": "601-800", "units": 200, "rate": 9.45, "cost": 1890},
            {"slab": "801-1000", "units": slab6, "rate": 10.50, "cost": round(slab6 * 10.50, 2)}
        ]

        else:
            slab2 = 200
            slab3 = 100
            slab4 = 100
            slab5 = 200
            slab6 = 200
            slab7 = units_consumed - 1000

            amount_due = (
            (slab2 * 4.70)
            + (slab3 * 6.30)
            + (slab4 * 8.40)
            + (slab5 * 9.45)
            + (slab6 * 10.50)
            + (slab7 * 11.55)
        )

            cost_breakdown = [
            {"slab": "0-200", "units": 200, "rate": 0, "cost": 0},
            {"slab": "201-400", "units": 200, "rate": 4.70, "cost": 940},
            {"slab": "401-500", "units": 100, "rate": 6.30, "cost": 630},
            {"slab": "501-600", "units": 100, "rate": 8.40, "cost": 840},
            {"slab": "601-800", "units": 200, "rate": 9.45, "cost": 1890},
            {"slab": "801-1000", "units": 200, "rate": 10.50, "cost": 2100},
            {"slab": "Above 1000", "units": slab7, "rate": 11.55, "cost": round(slab7 * 11.55, 2)}
        ]

    elif tariff == "commercial":
        amount_due = units_consumed * 8.0
        cost_breakdown = [
        {
            "slab": "Commercial",
            "units": units_consumed,
            "rate": 8.00,
            "cost": round(amount_due, 2)
        }
    ]

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid tariff category."
        )

    return {
    "amount_due": round(amount_due, 2),
    "cost_breakdown": cost_breakdown
}
    

@router.post("/upload-bill", response_model=UploadBillResponse)
async def upload_bill(
    consumer_number: Optional[str] = Form(None), 
    bill_month: Optional[date] = Form(None),
    tariff_category: Optional[str] = Form(None),
    units_consumed: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        ai_summary = "Manual Entry — insufficient data for AI analysis."
        saving_tips = ["Conserve appliance usage where possible."]

        if file:
            pipeline_results = await run_complete_student2_pipeline(file)

            # Map values extracted by Student 2
            consumer_number = pipeline_results["consumer_number"]
            bill_month = pipeline_results["bill_month"]
            units_consumed = pipeline_results["units_consumed"]
            tariff_category = pipeline_results["tariff_category"]

            # Map values generated by Student 3
            ai_summary = pipeline_results["ai_summary"]
            saving_tips = pipeline_results["saving_tips"]

        elif units_consumed is not None and tariff_category is not None and consumer_number is not None:
            manual_results = await generate_tips_for_manual_entry(
                units_consumed=units_consumed,
                tariff_category=tariff_category
            )
            ai_summary = manual_results["ai_summary"]
            saving_tips = manual_results["saving_tips"]

        # Validate that we have all core variables needed
        if any(v is None for v in [consumer_number, bill_month, tariff_category, units_consumed]):
            raise HTTPException(
                status_code=400,
                detail="Missing required bill fields. Please provide a valid file or complete all form fields including consumer number."
            )
        # Validate consumer number
        consumer_number = consumer_number.strip()
        if not consumer_number.isdigit():
            raise HTTPException(status_code=400,detail="Consumer number must contain only digits.")

        if len(consumer_number) not in (10, 12):
            raise HTTPException(status_code=400, detail="Consumer number must be 10 or 12 digits.")
        region_code=consumer_number[:2]
        region_name=REGION_MAP.get(region_code)
        if region_name is None:
            raise HTTPException(status_code=400,detail="Invalid consumer number. Unknown region code.")
        # Look up or create the User mapped to this consumer number
        user = db.query(models.User).filter(models.User.consumer_number == consumer_number).first()
        
        if not user:
            email_slug = "".join(e for e in consumer_number if e.isalnum())
            # FIX: Do not pass an explicit 'id' attribute here. 
            # Let the database handle auto-increment sequences cleanly.
            user = models.User(consumer_number=consumer_number,name=f"User_{consumer_number}",email=f"user_{email_slug}@example.com")
            db.add(user)
            try:
                db.commit()
                db.refresh(user)
            except Exception:
                db.rollback()
                # Safe fallback if concurrent requests attempt creation simultaneously
                user = db.query(models.User).filter(models.User.consumer_number == consumer_number).first()
    
        bill = calculate_amount_due(units_consumed=units_consumed, tariff_category=tariff_category)
        amount_due=bill["amount_due"]
        cost_breakdown=bill["cost_breakdown"]
        
        # Save bill records to the database
        new_bill = models.Bill(consumer_number=user.consumer_number,region=region_name,bill_month=bill_month,tariff_category=tariff_category,units_consumed=units_consumed,amount_due=amount_due,cost_breakdown=cost_breakdown)
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)

        # Save the analysis data
        new_analysis = models.Analysis(
            bill_id=new_bill.id,
            ai_summary=ai_summary,
            saving_tips=saving_tips
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

        return UploadBillResponse(
    consumer_number=new_bill.consumer_number,
    region=new_bill.region,
    tariff_category=new_bill.tariff_category,
    units_consumed=new_bill.units_consumed,
    amount_due=new_bill.amount_due,
    bill_month=str(new_bill.bill_month),
    ai_summary=new_analysis.ai_summary,
    saving_tips=new_analysis.saving_tips,
    cost_breakdown=new_bill.cost_breakdown
)

    except HTTPException:
        raise
    except AIServiceUnavailableError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
