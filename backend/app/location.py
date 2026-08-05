"""
location.py
===========
Geocoding and timezone resolution.

Uses:
  - OpenStreetMap Nominatim for geocoding (free, no API key)
  - timezonefinder for lat/lng → IANA timezone string

All functions are async for use with FastAPI's async endpoints.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx
from timezonefinder import TimezoneFinder

from app.models import GeoLocation

logger = logging.getLogger(__name__)

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_HEADERS = {
    "User-Agent": "StartRightDay/1.0 (contact@startrightday.app)"
}
_GEOCODE_TIMEOUT_SECONDS = 10

_tf = TimezoneFinder()


async def geocode_place(place_name: str) -> GeoLocation:
    """
    Resolve a human-readable place name to lat/lng and IANA timezone.

    Args:
        place_name: City or town name (e.g., "Mumbai", "New Delhi, India").

    Returns:
        GeoLocation with resolved coordinates and timezone.

    Raises:
        ValueError: If place cannot be geocoded or timezone cannot be determined.
    """
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }

    try:
        async with httpx.AsyncClient(timeout=_GEOCODE_TIMEOUT_SECONDS) as client:
            response = await client.get(
                _NOMINATIM_URL,
                params=params,
                headers=_NOMINATIM_HEADERS,
            )
            response.raise_for_status()
            results = response.json()
    except httpx.TimeoutException as exc:
        raise ValueError(
            f"Geocoding timed out for '{place_name}'. Please check your internet connection."
        ) from exc
    except httpx.HTTPError as exc:
        raise ValueError(
            f"Geocoding request failed for '{place_name}': {exc}"
        ) from exc

    if not results:
        raise ValueError(
            f"Place '{place_name}' not found. Please try a more specific name "
            f"(e.g., 'Mumbai, India' instead of 'Mumbai')."
        )

    top = results[0]
    latitude = float(top["lat"])
    longitude = float(top["lon"])
    display_name: str = top.get("display_name", place_name)

    timezone = _resolve_timezone(latitude, longitude, place_name)

    logger.info(
        "Geocoded '%s' → lat=%.4f, lng=%.4f, tz=%s",
        place_name,
        latitude,
        longitude,
        timezone,
    )

    return GeoLocation(
        place_name=display_name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )


def _resolve_timezone(lat: float, lng: float, original_name: str) -> str:
    """
    Resolve lat/lng to an IANA timezone string using timezonefinder.

    Raises:
        ValueError: If timezone cannot be determined (e.g., ocean coordinates).
    """
    tz: Optional[str] = _tf.timezone_at(lat=lat, lng=lng)
    if tz is None:
        # Attempt closest timezone (handles edge cases near coastlines)
        tz = _tf.closest_timezone_at(lat=lat, lng=lng)
    if tz is None:
        raise ValueError(
            f"Could not determine timezone for '{original_name}' "
            f"(lat={lat:.4f}, lng={lng:.4f}). Please provide a more specific location."
        )
    return tz
