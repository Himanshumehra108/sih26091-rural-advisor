from pydantic import BaseModel


class FeasibilityRequest(BaseModel):
    business_type: str
    location: str
    available_capital: float


class SWOTResponse(BaseModel):
    strengths: list[str] = []
    weaknesses: list[str] = []
    opportunities: list[str] = []
    threats: list[str] = []


class ReportOutput(BaseModel):
    title: str
    summary: str
    swot: SWOTResponse
