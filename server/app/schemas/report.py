# server/app/schemas/report.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


class LocationInput(BaseModel):
    village: str
    block: str
    district: str
    state: str


class ReportCreate(BaseModel):
    business_category: str
    available_margin: float
    location: LocationInput
    calculator_result: Optional[Dict[str, Any]] = None
    advisory_result: Optional[Dict[str, Any]] = None


class ReportOut(BaseModel):
    id: str
    business_category: str
    available_margin: float
    location: Dict[str, Any]
    calculator_result: Optional[Dict[str, Any]]
    advisory_result: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True