# server/app/api/v1/routes_reports.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report
from app.schemas.report import ReportCreate

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/")
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_report = Report(
        user_id=current_user.id,
        business_category=payload.business_category,
        available_margin=payload.available_margin,
        location=payload.location.dict(),
        calculator_result=payload.calculator_result,
        advisory_result=payload.advisory_result,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {"success": True, "data": {"report_id": str(new_report.id)}, "error": None}


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = db.query(Report).filter(Report.user_id == current_user.id).all()
    result = [
        {
            "report_id": str(r.id),
            "business_category": r.business_category,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]
    return {"success": True, "data": result, "error": None}


@router.get("/{report_id}")
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(
        Report.id == report_id, Report.user_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "success": True,
        "data": {
            "id": str(report.id),
            "business_category": report.business_category,
            "available_margin": report.available_margin,
            "location": report.location,
            "calculator_result": report.calculator_result,
            "advisory_result": report.advisory_result,
        },
        "error": None,
    }