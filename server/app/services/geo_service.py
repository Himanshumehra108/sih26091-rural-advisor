# server/app/services/geo_service.py
"""Places and routing backbone for advisory (Nominatim + Overpass + OSRM)."""

from __future__ import annotations

import logging
import math
import threading
import time
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from app.core.config import settings
from app.core.constants import DEFAULT_MARKET_RADIUS_KM

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0
MAX_ROUTED_PLACES = 40
OSM_COUNTRY = "in"

# OSM tags treated as competing outlets per business category.
CATEGORY_TAGS: dict[str, list[tuple[str, str]]] = {
    "Dairy": [
        ("shop", "dairy"),
        ("shop", "cheese"),
        ("shop", "convenience"),
        ("amenity", "marketplace"),
    ],
    "Retail": [
        ("shop", "convenience"),
        ("shop", "supermarket"),
        ("shop", "general"),
        ("shop", "kiosk"),
        ("shop", "variety_store"),
        ("amenity", "marketplace"),
    ],
    "Textiles": [
        ("shop", "clothes"),
        ("shop", "fabric"),
        ("shop", "textile"),
        ("shop", "fashion_accessories"),
    ],
    "Food Processing": [
        ("shop", "bakery"),
        ("shop", "confectionery"),
        ("shop", "food"),
        ("amenity", "marketplace"),
    ],
    "Handicrafts": [
        ("shop", "craft"),
        ("shop", "gift"),
        ("shop", "art"),
    ],
    "Poultry": [
        ("shop", "butcher"),
        ("shop", "farm"),
        ("amenity", "marketplace"),
    ],
    "Agriculture Inputs": [
        ("shop", "agrarian"),
        ("shop", "farm"),
        ("shop", "garden_centre"),
        ("shop", "hardware"),
    ],
    "Tailoring": [
        ("shop", "tailor"),
        ("shop", "clothes"),
        ("craft", "tailor"),
    ],
    "Transport": [
        ("amenity", "bus_station"),
        ("amenity", "taxi"),
        ("amenity", "fuel"),
        ("shop", "car_repair"),
    ],
    "Other": [
        ("amenity", "marketplace"),
        ("shop", "convenience"),
        ("shop", "general"),
    ],
}

CHANNEL_TAGS: list[tuple[str, str]] = [
    ("amenity", "marketplace"),
    ("amenity", "bus_station"),
    ("shop", "wholesale"),
]

SETTLEMENT_REGEX = "city|town|village|hamlet|suburb"

POPULATION_DEFAULTS = {
    "city": 50000,
    "town": 8000,
    "suburb": 3000,
    "village": 1500,
    "hamlet": 400,
}

_client: httpx.Client | None = None
_nominatim_lock = threading.Lock()
_last_nominatim_at = 0.0


def _http() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=httpx.Timeout(settings.geo_http_timeout_seconds),
            headers={
                "User-Agent": settings.osm_user_agent,
                "Accept": "application/json",
            },
            follow_redirects=True,
        )
    return _client


def _client_or_default(client: httpx.Client | None) -> httpx.Client:
    return client if client is not None else _http()


def location_query(location: str | Mapping[str, Any]) -> str:
    """Flatten a village/block/district/state payload into a Nominatim query."""
    if isinstance(location, str):
        return location.strip()
    parts: list[str] = []
    for key in ("village", "block", "district", "state"):
        value = location.get(key)
        if value:
            parts.append(str(value).strip())
    if parts:
        return ", ".join(parts)
    return str(location.get("location") or location.get("q") or "").strip()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def saturation_level(count: int) -> str:
    if count <= 2:
        return "low"
    if count <= 8:
        return "medium"
    return "high"


def _throttle_nominatim() -> None:
    global _last_nominatim_at
    interval = settings.nominatim_min_interval_seconds
    if interval <= 0:
        return
    with _nominatim_lock:
        wait = interval - (time.monotonic() - _last_nominatim_at)
        if wait > 0:
            time.sleep(wait)
        _last_nominatim_at = time.monotonic()


def geocode(
    location: str | Mapping[str, Any],
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Forward-geocode a place name with Nominatim (OpenStreetMap)."""
    query = location_query(location)
    if not query:
        raise ValueError("Location is required for geocoding.")

    _throttle_nominatim()
    http = _client_or_default(client)
    url = settings.nominatim_base_url.rstrip("/") + "/search"
    response = http.get(
        url,
        params={
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": OSM_COUNTRY,
        },
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        raise ValueError(f"No geocoding result for '{query}'.")

    hit = results[0]
    return {
        "query": query,
        "lat": float(hit["lat"]),
        "lon": float(hit["lon"]),
        "display_name": hit.get("display_name") or query,
        "osm_type": hit.get("osm_type"),
        "osm_id": hit.get("osm_id"),
        "address": hit.get("address") or {},
    }


def _category_filters(business_category: str | None) -> list[tuple[str, str]]:
    key = (business_category or "Other").strip()
    tags = list(CATEGORY_TAGS.get(key, CATEGORY_TAGS["Other"]))
    seen = set(tags)
    for extra in CHANNEL_TAGS:
        if extra not in seen:
            tags.append(extra)
            seen.add(extra)
    return tags


def _overpass_query(lat: float, lon: float, radius_m: int, business_category: str | None) -> str:
    clauses: list[str] = [
        f'nwr["place"~"{SETTLEMENT_REGEX}"](around:{radius_m},{lat},{lon});'
    ]
    for key, value in _category_filters(business_category):
        clauses.append(f'nwr["{key}"="{value}"](around:{radius_m},{lat},{lon});')
    body = "\n  ".join(clauses)
    return f"[out:json][timeout:25];\n(\n  {body}\n);\nout center tags;"


def _coords_from_element(element: Mapping[str, Any]) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center") or {}
    if "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None


def _channel_labels(tags: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    amenity = tags.get("amenity")
    shop = tags.get("shop")
    if amenity == "marketplace":
        labels.append("local haat")
        labels.append("nearby mandi")
    if amenity == "bus_station":
        labels.append("nearby transport hub")
    if shop == "wholesale":
        labels.append("wholesale market")
    return labels


def _is_competitor(tags: Mapping[str, Any], business_category: str | None) -> bool:
    if tags.get("place"):
        return False
    pair = None
    for key in ("shop", "amenity", "craft"):
        if key in tags:
            pair = (key, str(tags[key]))
            break
    if pair is None:
        return False
    category_key = (business_category or "Other").strip()
    return pair in CATEGORY_TAGS.get(category_key, CATEGORY_TAGS["Other"])


def _settlement_population(tags: Mapping[str, Any]) -> int:
    raw = tags.get("population")
    if raw:
        digits = "".join(ch for ch in str(raw) if ch.isdigit())
        if digits:
            return int(digits)
    place = str(tags.get("place") or "")
    return POPULATION_DEFAULTS.get(place, 0)


def parse_overpass_elements(
    elements: Sequence[Mapping[str, Any]],
    origin: Mapping[str, float],
    business_category: str | None,
) -> list[dict[str, Any]]:
    """Normalize Overpass nodes/ways into advisory place records."""
    origin_lat = float(origin["lat"])
    origin_lon = float(origin["lon"])
    places: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()

    for element in elements:
        osm_type = str(element.get("type") or "node")
        osm_id = int(element.get("id") or 0)
        key = (osm_type, osm_id)
        if key in seen:
            continue
        coords = _coords_from_element(element)
        if coords is None:
            continue
        seen.add(key)
        lat, lon = coords
        tags = dict(element.get("tags") or {})
        name = tags.get("name") or tags.get("name:en") or tags.get("name:hi") or "Unnamed place"
        kind = "settlement" if tags.get("place") else "poi"
        channels = _channel_labels(tags)
        competitor = _is_competitor(tags, business_category)
        role = "settlement" if kind == "settlement" else (
            "distribution_channel" if channels and not competitor else (
                "competitor" if competitor else "nearby_place"
            )
        )
        places.append({
            "id": f"{osm_type}/{osm_id}",
            "name": name,
            "kind": kind,
            "role": role,
            "lat": lat,
            "lon": lon,
            "straight_line_km": round(haversine_km(origin_lat, origin_lon, lat, lon), 3),
            "tags": {
                key: tags[key]
                for key in ("shop", "amenity", "craft", "place", "population")
                if key in tags
            },
            "channels": channels,
            "is_competitor": competitor,
            "estimated_population": _settlement_population(tags) if kind == "settlement" else None,
        })

    places.sort(key=lambda item: item["straight_line_km"])
    return places


def search_places(
    lat: float,
    lon: float,
    radius_km: float,
    business_category: str | None = None,
    *,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    """Search nearby OSM features with the Overpass API."""
    radius_m = max(int(radius_km * 1000), 500)
    query = _overpass_query(lat, lon, radius_m, business_category)
    http = _client_or_default(client)
    response = http.post(settings.overpass_url, data={"data": query})
    response.raise_for_status()
    payload = response.json()
    return parse_overpass_elements(
        payload.get("elements") or [],
        {"lat": lat, "lon": lon},
        business_category,
    )


def parse_osrm_table(
    payload: Mapping[str, Any],
    destinations: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Attach driving distance (km) and duration (minutes) from OSRM Table."""
    if str(payload.get("code") or "").lower() != "ok":
        raise ValueError(f"OSRM table failed: {payload.get('code')}")

    distances = (payload.get("distances") or [[]])[0]
    durations = (payload.get("durations") or [[]])[0]
    routed: list[dict[str, Any]] = []
    for index, place in enumerate(destinations):
        # sources=0, so destination i is column i+1 (column 0 is the origin).
        column = index + 1
        meters = distances[column] if column < len(distances) else None
        seconds = durations[column] if column < len(durations) else None
        record = dict(place)
        if meters is None:
            record["road_distance_km"] = record.get("straight_line_km")
            record["travel_minutes"] = None
            record["distance_source"] = "haversine"
        else:
            record["road_distance_km"] = round(float(meters) / 1000.0, 3)
            record["travel_minutes"] = None if seconds is None else round(float(seconds) / 60.0, 1)
            record["distance_source"] = "osrm"
        routed.append(record)
    return routed


def driving_distances(
    origin: Mapping[str, float],
    destinations: Sequence[Mapping[str, Any]],
    *,
    client: httpx.Client | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Road distances from origin to each destination via OSRM, with haversine fallback."""
    if not destinations:
        return [], "none"

    coords = [f"{origin['lon']},{origin['lat']}"]
    coords.extend(f"{place['lon']},{place['lat']}" for place in destinations)
    http = _client_or_default(client)
    url = settings.osrm_base_url.rstrip("/") + f"/table/v1/driving/{';'.join(coords)}"
    try:
        response = http.get(url, params={"sources": "0", "annotations": "duration,distance"})
        response.raise_for_status()
        routed = parse_osrm_table(response.json(), destinations)
        source = "osrm" if any(item.get("distance_source") == "osrm" for item in routed) else "haversine"
        return routed, source
    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
        logger.warning("OSRM table unavailable, using straight-line distances: %s", exc)
        fallback = []
        for place in destinations:
            record = dict(place)
            record["road_distance_km"] = record.get("straight_line_km")
            record["travel_minutes"] = None
            record["distance_source"] = "haversine"
            fallback.append(record)
        return fallback, "haversine"


def _consumer_base(places: Sequence[Mapping[str, Any]]) -> int:
    total = 0
    for place in places:
        if place.get("kind") == "settlement":
            total += int(place.get("estimated_population") or 0)
    return total


def _unique_channels(places: Sequence[Mapping[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for place in places:
        for label in place.get("channels") or []:
            if label not in seen:
                seen.add(label)
                ordered.append(label)
    if "direct doorstep" not in seen:
        ordered.append("direct doorstep")
    return ordered


def market_reach(
    location: str | Mapping[str, Any],
    radius_km: float = DEFAULT_MARKET_RADIUS_KM,
    business_category: str | None = None,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Geocode a location, find nearby places, and attach road distances."""
    origin = geocode(location, client=client)
    try:
        places = search_places(
            origin["lat"],
            origin["lon"],
            radius_km,
            business_category,
            client=client,
        )
    except httpx.HTTPError as exc:
        logger.warning("Overpass search failed: %s", exc)
        places = []

    settlements = [place for place in places if place["kind"] == "settlement"]
    pois = [place for place in places if place["kind"] != "settlement"]
    to_route = (pois + settlements)[:MAX_ROUTED_PLACES]
    routed, distance_source = driving_distances(origin, to_route, client=client)

    routed_pois = [place for place in routed if place["kind"] != "settlement"]
    routed_settlements = [place for place in routed if place["kind"] == "settlement"]
    competitors = [place for place in routed_pois if place.get("is_competitor")]

    return {
        "location": origin["query"],
        "origin": {
            "lat": origin["lat"],
            "lon": origin["lon"],
            "display_name": origin["display_name"],
        },
        "radius_km": radius_km,
        "estimated_consumer_base": _consumer_base(routed_settlements),
        "distribution_channels": _unique_channels(routed_pois),
        "places": routed_pois,
        "settlements": routed_settlements,
        "competitors": competitors,
        "competitor_density": {
            "estimated_count": len(competitors),
            "saturation_level": saturation_level(len(competitors)),
        },
        "distance_source": distance_source,
    }


def competitor_density(
    location: str | Mapping[str, Any],
    radius_km: float = DEFAULT_MARKET_RADIUS_KM,
    business_category: str | None = None,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Competitor count and saturation derived from Overpass POIs + OSRM reach."""
    reach = market_reach(location, radius_km, business_category, client=client)
    return {
        "location": reach["location"],
        "origin": reach["origin"],
        "radius_km": reach["radius_km"],
        "competitors": reach["competitors"],
        "estimated_count": reach["competitor_density"]["estimated_count"],
        "saturation_level": reach["competitor_density"]["saturation_level"],
        "distance_source": reach["distance_source"],
    }
