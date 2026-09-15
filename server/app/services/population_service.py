"""Population lookup using explicit population tags from geocoded OSM settlements.

OSM is used only when it provides a numeric population tag. Missing data is
reported as unavailable; this service never invents estimates.
"""

from __future__ import annotations

import logging
import csv
import io
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

logger = logging.getLogger(__name__)
SOURCE = "OpenStreetMap population tag"
CENSUS_SOURCE = "Census of India 2011 district dataset"
CENSUS_DATA_URL = "https://raw.githubusercontent.com/vanshchauhan1/Indian-Census-2011-Data-Analysis/master/data2.csv"
_census_cache: list[dict[str, Any]] | None = None


def _normalized(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _population_value(place: Mapping[str, Any]) -> int | None:
    value = place.get("estimated_population")
    if isinstance(value, bool) or value is None:
        return None
    try:
        population = int(value)
    except (TypeError, ValueError):
        return None
    return population if population > 0 else None


def _unavailable(status: str = "unavailable") -> dict[str, Any]:
    return {
        "population": None,
        "population_level": None,
        "area_name": None,
        "source": None,
        "year": None,
        "status": status,
    }


def _load_census_districts() -> list[dict[str, Any]]:
    global _census_cache
    if _census_cache is not None:
        return _census_cache
    try:
        response = httpx.get(CENSUS_DATA_URL, timeout=15)
        response.raise_for_status()
        records: list[dict[str, Any]] = []
        for row in csv.DictReader(io.StringIO(response.text)):
            district = _normalized(row.get("District"))
            state = _normalized(row.get("State"))
            raw_population = str(row.get("Population") or "").replace(",", "").strip()
            if not district or not state or not raw_population.isdigit():
                continue
            records.append({
                "district": district,
                "state": state,
                "population": int(raw_population),
            })
        _census_cache = records
    except (httpx.HTTPError, ValueError, csv.Error) as exc:
        logger.warning("Census population lookup unavailable: %s", exc)
        _census_cache = []
    return _census_cache


def _census_district_population(state: str | None, district: str | None) -> dict[str, Any]:
    state_key = _normalized(state)
    district_key = _normalized(district)
    if not state_key or not district_key:
        return _unavailable()
    for row in _load_census_districts():
        if row["state"] == state_key and row["district"] == district_key:
            return {
                "population": row["population"],
                "population_level": "district",
                "area_name": district,
                "source": CENSUS_SOURCE,
                "year": 2011,
                "status": "success",
            }
    return _unavailable()


def get_population(
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    state: str | None = None,
    district: str | None = None,
    village: str | None = None,
    pincode: str | None = None,
    places: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the most specific explicitly sourced population available.

    ``places`` is the already geocoded/nearby OSM result from geo_service. The
    arguments are retained as a stable service contract for a future Census
    adapter, but no fallback number is generated when data is absent.
    """
    del latitude, longitude, pincode
    settlements = [place for place in (places or []) if place.get("kind") == "settlement"]
    with_population = [place for place in settlements if _population_value(place) is not None]
    if not with_population:
        return _census_district_population(state, district)

    requested_village = _normalized(village)
    if requested_village:
        exact = [
            place for place in with_population
            if _normalized(place.get("name")) == requested_village
        ]
        if exact:
            selected = exact[0]
            level = "village" if selected.get("tags", {}).get("place") == "village" else "town"
        else:
            # Village data is not available, so use the authoritative
            # district fallback rather than an unrelated nearby settlement.
            return _census_district_population(state, district)
    else:
        selected = None

    if selected is None:
        if not requested_village:
            census_result = _census_district_population(state, district)
            if census_result["status"] == "success":
                return census_result
        selected = min(
            with_population,
            key=lambda place: float(place.get("straight_line_km") or float("inf")),
        )
        place_type = selected.get("tags", {}).get("place")
        level = "village" if place_type in {"village", "hamlet"} else "town"

    return {
        "population": _population_value(selected),
        "population_level": level,
        "area_name": selected.get("name"),
        "source": SOURCE,
        "year": None,
        "status": "success",
    }
