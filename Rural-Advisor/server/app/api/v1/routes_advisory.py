# server/app/api/v1/routes_advisory.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.constants import DEFAULT_MARKET_RADIUS_KM
from app.services.geo_service import market_reach as geo_market_reach

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
    # TEMPORARY DUMMY DATA — SWOT/pricing still placeholders until RAG + LLM (Module 1)
    market = {
        "radius_km": DEFAULT_MARKET_RADIUS_KM,
        "estimated_consumer_base": 4200,
        "distribution_channels": ["local haat", "direct doorstep", "nearby mandi"],
    }
    competitors = {"estimated_count": 6, "saturation_level": "medium"}
    try:
        geo = geo_market_reach(
            payload.location.model_dump(),
            DEFAULT_MARKET_RADIUS_KM,
            payload.business_category,
        )
        market = {
            "radius_km": geo["radius_km"],
            "estimated_consumer_base": geo["estimated_consumer_base"],
            "distribution_channels": geo["distribution_channels"],
            "origin": geo["origin"],
            "places": geo["places"][:15],
            "distance_source": geo["distance_source"],
        }
        competitors = geo["competitor_density"]
    except Exception:
        pass

    return {
        "success": True,
        "data": {
            "market_reach": market,
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
            "competitor_density": competitors,
            "pricing_suggestion": {
                "suggested_price_range": "₹40–55 per unit",
                "reasoning": "Based on regional purchasing power and existing competitor pricing in the block.",
            },
        },
        "error": None,
    }