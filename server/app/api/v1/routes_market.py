from fastapi import APIRouter

router = APIRouter(prefix='/market', tags=['market'])


@router.get('/competitor-density')
def competitor_density(location: str):
    return {'location': location, 'competitors': []}


@router.get('/market-reach')
def market_reach(location: str, radius_km: float = 5):
    return {'location': location, 'radius_km': radius_km}
