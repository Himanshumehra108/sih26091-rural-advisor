from app.services.geo_service import (
    haversine_km,
    location_query,
    market_reach,
    parse_osrm_table,
    parse_overpass_elements,
    saturation_level,
)


def test_location_query_joins_admin_parts():
    query = location_query({
        "village": "Sinnar",
        "block": "Sinnar",
        "district": "Nashik",
        "state": "Maharashtra",
    })
    assert query == "Sinnar, Sinnar, Nashik, Maharashtra"


def test_haversine_same_point_is_zero():
    assert haversine_km(19.99, 73.78, 19.99, 73.78) == 0


def test_saturation_bands():
    assert saturation_level(1) == "low"
    assert saturation_level(6) == "medium"
    assert saturation_level(12) == "high"


def test_parse_overpass_classifies_competitors_and_settlements():
    elements = [
        {
            "type": "node",
            "id": 1,
            "lat": 20.0,
            "lon": 73.8,
            "tags": {"name": "Local Dairy", "shop": "dairy"},
        },
        {
            "type": "way",
            "id": 2,
            "center": {"lat": 20.01, "lon": 73.81},
            "tags": {"name": "Village Haat", "amenity": "marketplace"},
        },
        {
            "type": "node",
            "id": 3,
            "lat": 20.02,
            "lon": 73.79,
            "tags": {"name": "Sinnar", "place": "village", "population": "12000"},
        },
    ]
    places = parse_overpass_elements(elements, {"lat": 19.99, "lon": 73.78}, "Dairy")
    by_id = {place["id"]: place for place in places}

    assert by_id["node/1"]["is_competitor"] is True
    assert by_id["node/1"]["role"] == "competitor"
    assert "local haat" in by_id["way/2"]["channels"]
    assert by_id["node/3"]["kind"] == "settlement"
    assert by_id["node/3"]["estimated_population"] == 12000
    assert places[0]["straight_line_km"] <= places[-1]["straight_line_km"]


def test_parse_osrm_table_attaches_road_metrics():
    destinations = [
        {"name": "Haat", "straight_line_km": 2.5},
        {"name": "Dairy", "straight_line_km": 4.0},
    ]
    payload = {
        "code": "Ok",
        "distances": [[0, 3200, None]],
        "durations": [[0, 480, None]],
    }
    routed = parse_osrm_table(payload, destinations)
    assert routed[0]["road_distance_km"] == 3.2
    assert routed[0]["travel_minutes"] == 8.0
    assert routed[0]["distance_source"] == "osrm"
    assert routed[1]["road_distance_km"] == 4.0
    assert routed[1]["distance_source"] == "haversine"


def test_market_reach_composes_nominatim_overpass_osrm(monkeypatch):
    import json

    import httpx

    from app.core.config import settings

    monkeypatch.setattr(settings, "nominatim_min_interval_seconds", 0)

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "/search" in url:
            return httpx.Response(
                200,
                json=[{
                    "lat": "19.99",
                    "lon": "73.78",
                    "display_name": "Sinnar, Nashik, Maharashtra, India",
                    "osm_type": "relation",
                    "osm_id": 99,
                    "address": {"state": "Maharashtra"},
                }],
            )
        if "overpass" in url or "interpreter" in url:
            return httpx.Response(
                200,
                json={
                    "elements": [
                        {
                            "type": "node",
                            "id": 11,
                            "lat": 20.0,
                            "lon": 73.79,
                            "tags": {"name": "Krupa Dairy", "shop": "dairy"},
                        },
                        {
                            "type": "node",
                            "id": 12,
                            "lat": 20.01,
                            "lon": 73.80,
                            "tags": {"name": "Weekly Haat", "amenity": "marketplace"},
                        },
                        {
                            "type": "node",
                            "id": 13,
                            "lat": 20.02,
                            "lon": 73.77,
                            "tags": {"name": "Nearby village", "place": "village", "population": "2500"},
                        },
                    ]
                },
            )
        if "/table/v1/driving/" in url:
            return httpx.Response(
                200,
                json={
                    "code": "Ok",
                    "distances": [[0, 1500, 2400, 3600]],
                    "durations": [[0, 180, 300, 420]],
                },
            )
        return httpx.Response(404, json={"error": url})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    result = market_reach("Sinnar, Nashik", radius_km=7, business_category="Dairy", client=client)

    assert result["origin"]["lat"] == 19.99
    assert result["estimated_consumer_base"] == 2500
    assert result["competitor_density"]["estimated_count"] >= 1
    assert "direct doorstep" in result["distribution_channels"]
    assert result["distance_source"] == "osrm"
    assert result["places"][0]["road_distance_km"] == 1.5
    json.dumps(result)

