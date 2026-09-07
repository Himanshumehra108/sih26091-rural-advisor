# server/app/api/v1/routes_calculator.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.scheme_selector import select_scheme
from app.services.emi_engine import calculate_quarterly_emi

router = APIRouter(prefix="/calculator", tags=["Calculator"])


class EligibilityRequest(BaseModel):
    available_margin: float = Field(..., gt=0, description="User's available margin capital in ₹")


class EMIRequest(BaseModel):
    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0)
    tenure_years: int = Field(..., gt=0)
    moratorium_months: int = Field(..., ge=0)


@router.post("/calculate-eligibility")
def calculate_eligibility(payload: EligibilityRequest):
    try:
        result = select_scheme(payload.available_margin)
        return {"success": True, "data": result, "error": None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emi-schedule")
def emi_schedule(payload: EMIRequest):
    try:
        result = calculate_quarterly_emi(
            loan_amount=payload.loan_amount,
            annual_interest_rate=payload.interest_rate,
            tenure_years=payload.tenure_years,
            moratorium_months=payload.moratorium_months,
        )
        return {"success": True, "data": result, "error": None}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))