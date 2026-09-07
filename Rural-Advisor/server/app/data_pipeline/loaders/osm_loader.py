def load_osm(location: str) -> list[dict]:
    from app.services.geo_service import market_reach

    return market_reach(location).get("places") or []
