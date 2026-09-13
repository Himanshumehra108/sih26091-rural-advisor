from fastapi import APIRouter, HTTPException, Query

from app.core.constants import DEFAULT_MARKET_RADIUS_KM
from app.services.geo_service import competitor_density as geo_competitor_density
from app.services.geo_service import market_reach as geo_market_reach

router = APIRouter(prefix='/market', tags=['market'])


@router.get('/competitor-density')
def competitor_density(
    location: str,
    business_category: str | None = None,
    radius_km: float = Query(DEFAULT_MARKET_RADIUS_KM, gt=0, le=50),
):
    try:
        return geo_competitor_density(location, radius_km, business_category)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get('/market-reach')
def market_reach(
    location: str,
    business_category: str | None = None,
    radius_km: float = Query(DEFAULT_MARKET_RADIUS_KM, gt=0, le=50),
):
    try:
        return geo_market_reach(location, radius_km, business_category)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
