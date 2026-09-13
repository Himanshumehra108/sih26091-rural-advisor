from pydantic import BaseModel, Field


class MarginInput(BaseModel):
    available_capital: float = Field(gt=0)


class SchemeOutput(BaseModel):
    name: str
    eligible_amount: float
    annual_rate: float
    tenure_months: int


class EMIResponse(BaseModel):
    monthly_emi: float
    schedule: list[dict]
