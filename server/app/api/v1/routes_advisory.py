# server/app/api/v1/routes_advisory.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/advisory", tags=["Advisory"])


class LocationInput(BaseModel):
    village: str
    block: str
    district: str
    state: str


class FeasibilityRequest(BaseModel):
    location: LocationInput
    available_margin: float
    business_category: str
    language: str = "en"


@router.post("/feasibility-report")
def feasibility_report(payload: FeasibilityRequest):
    # TEMPORARY DUMMY DATA — real logic will call RAG + LLM (Module 1, owned by #4)
    return {
        "success": True,
        "data": {
            "market_reach": {
                "radius_km": 7,
                "estimated_consumer_base": 4200,
                "distribution_channels": ["local haat", "direct doorstep", "nearby mandi"],
            },
            "opportunity_analysis": f"There is unmet demand for {payload.business_category} in {payload.location.block}, particularly due to limited cold-chain access in the area.",
            "swot": {
                "strengths": ["Low competition in immediate radius", "Access to raw materials locally"],
                "weaknesses": ["Limited working capital for scale-up", "Seasonal demand fluctuation"],
                "opportunities": ["Growing demand from nearby urban markets", "Government scheme support available"],
                "threats": ["Dependency on a single buyer", "Price volatility in raw material sourcing"],
            },
            "threats": [
                "Seasonal demand drop during monsoon",
                "Single-buyer dependency risk",
            ],
            "competitor_density": {
                "estimated_count": 6,
                "saturation_level": "medium",
            },
            "pricing_suggestion": {
                "suggested_price_range": "₹40–55 per unit",
                "reasoning": "Based on regional purchasing power and existing competitor pricing in the block.",
            },
        },
        "error": None,
    }