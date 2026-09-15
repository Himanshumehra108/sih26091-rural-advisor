# server/app/api/v1/routes_advisory.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.constants import DEFAULT_MARKET_RADIUS_KM
from app.services.geo_service import market_reach as geo_market_reach
from app.services.llm_client import LLMError, analyze_feasibility, is_configured

router = APIRouter(prefix="/advisory", tags=["Advisory"])


class LocationInput(BaseModel):
    village: str
    block: str
    district: str
    state: str
    pincode: str | None = None


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
        "population": {
            "population": None,
            "population_level": None,
            "area_name": None,
            "source": None,
            "year": None,
            "status": "unavailable",
        },
        "estimated_consumer_base": None,
        "distribution_channels": ["local haat", "direct doorstep", "nearby mandi"],
    }
    competitors = {"estimated_count": 6, "saturation_level": "medium"}
    opportunity = (
        f"There is unmet demand for {payload.business_category} in {payload.location.block}, "
        "particularly due to limited cold-chain access in the area."
    )
    swot = {
        "strengths": ["Low competition in immediate radius", "Access to raw materials locally"],
        "weaknesses": ["Limited working capital for scale-up", "Seasonal demand fluctuation"],
        "opportunities": ["Growing demand from nearby urban markets", "Government scheme support available"],
        "threats": ["Dependency on a single buyer", "Price volatility in raw material sourcing"],
    }
    threats = [
        "Seasonal demand drop during monsoon",
        "Single-buyer dependency risk",
    ]
    pricing = {
        "suggested_price_range": "₹40–55 per unit",
        "reasoning": "Based on regional purchasing power and existing competitor pricing in the block.",
    }

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
            "population": geo["population"],
            "estimated_consumer_base": geo["estimated_consumer_base"],
        }
        competitors = geo["competitor_density"]
    except Exception:
        pass

    if is_configured():
        location_label = ", ".join(
            part for part in (
                payload.location.village,
                payload.location.block,
                payload.location.district,
                payload.location.state,
            ) if part
        )
        try:
            analysis = analyze_feasibility(
                business_category=payload.business_category,
                location_label=location_label,
                language=payload.language,
                context=(
                    f"Available margin: ₹{payload.available_margin}\n"
                    f"Market reach: {market}\n"
                    f"Competitor density: {competitors}"
                ),
            )
            opportunity = analysis.get("opportunity_analysis") or opportunity
            swot = analysis.get("swot") or swot
            threats = analysis.get("threats") or threats
            pricing = analysis.get("pricing_suggestion") or pricing
        except LLMError:
            pass

    return {
        "success": True,
        "data": {
            "market_reach": market,
            "opportunity_analysis": opportunity,
            "swot": swot,
            "threats": threats,
            "competitor_density": competitors,
            "pricing_suggestion": pricing,
        },
        "error": None,
    }