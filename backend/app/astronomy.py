"""
astronomy.py
============
Thin, pure wrappers around the Swiss Ephemeris (pyswisseph).

Design rules:
  - Every function is pure (no side effects, no global state mutations).
  - All inputs/outputs are plain Python types (float, datetime).
  - Lahiri (Chitrapaksha) Ayanamsa is applied for sidereal positions.
  - Julian Day numbers are in Universal Time (UT).
"""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Tuple

import swisseph as swe

# ---------------------------------------------------------------------------
# One-time ephemeris configuration
# Lahiri Ayanamsa = SE_SIDM_LAHIRI = 1
# ---------------------------------------------------------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)


def datetime_to_jd(dt: datetime) -> float:
    """
    Convert a timezone-aware datetime to a Julian Day number (UT).

    The datetime MUST be timezone-aware; naive datetimes will raise ValueError.
    """
    if dt.tzinfo is None:
        raise ValueError(
            f"datetime_to_jd requires timezone-aware datetime, got: {dt!r}"
        )
    # Convert to UTC first
    dt_utc = dt.astimezone(dt_timezone.utc)
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def get_planet_longitude_sidereal(jd_ut: float, planet: int) -> float:
    """
    Return the sidereal ecliptic longitude (degrees, 0–360) of a planet.

    Args:
        jd_ut:  Julian Day in Universal Time.
        planet: Swiss Ephemeris planet constant (e.g., swe.MOON, swe.SUN).

    Returns:
        Sidereal longitude in degrees [0, 360).
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd_ut, planet, flags)
    longitude: float = result[0] % 360.0
    return longitude


def get_moon_longitude(jd_ut: float) -> float:
    """Sidereal longitude of the Moon (degrees)."""
    return get_planet_longitude_sidereal(jd_ut, swe.MOON)


def get_sun_longitude(jd_ut: float) -> float:
    """Sidereal longitude of the Sun (degrees)."""
    return get_planet_longitude_sidereal(jd_ut, swe.SUN)


def get_moon_sun_longitudes(jd_ut: float) -> Tuple[float, float]:
    """
    Compute both Moon and Sun sidereal longitudes in a single call.

    Returns:
        (moon_longitude, sun_longitude) in degrees.
    """
    return get_moon_longitude(jd_ut), get_sun_longitude(jd_ut)
