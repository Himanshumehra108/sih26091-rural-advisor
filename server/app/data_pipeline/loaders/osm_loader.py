"""Loads nearby-places data for a location using the OSM market-reach
pipeline (Nominatim geocoding + Overpass places + OSRM distances) that
lives in app.services.geo_service.

Unlike the other loaders in this package, this one takes a location
name (village/block/district/state string) instead of a file path,
since this data is fetched live rather than read from a raw export.
"""

from __future__ import annotations

import logging

from app.services.geo_service import market_reach

logger = logging.getLogger(__name__)


def load_osm(location: str) -> list[dict]:
    """Fetch nearby places (competitors/channels/settlements) for `location`.

    Returns [] if `location` is blank or the geocoding/Overpass/OSRM
    pipeline fails (network issue, place not found, etc.) — callers
    should treat that as "no market-reach data available" rather than
    a fatal error that takes down the whole report.
    """
    if not location or not location.strip():
        return []

    try:
        result = market_reach(location.strip())
    except Exception:
        logger.exception("data_pipeline: market_reach failed for %r", location)
        return []

    return result.get("places") or []