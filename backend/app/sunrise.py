"""
sunrise.py
==========
Computes sunrise/sunset and the three inauspicious daytime periods:
  - Rahu Kalam
  - Yamaganda
  - Gulika Kalam

Uses the `astral` library for accurate sunrise/sunset calculations,
then applies classical Vedic fractional rules for the inauspicious periods.

All returned datetimes are timezone-aware.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Tuple

import pytz
from astral import LocationInfo
from astral.sun import sun

from app.constants import (
    GULIKA_KALAM_PARTS,
    INAUSPICIOUS_PERIOD_PARTS,
    RAHU_KALAM_PARTS,
    YAMAGANDA_PARTS,
)


def get_sunrise_sunset(
    lat: float,
    lng: float,
    activity_date: date,
    timezone: str,
) -> Tuple[datetime, datetime]:
    """
    Return (sunrise, sunset) as timezone-aware datetimes.

    Args:
        lat:           Latitude of the location.
        lng:           Longitude of the location.
        activity_date: The calendar date for which to compute sunrise/sunset.
        timezone:      IANA timezone string (e.g., "Asia/Kolkata").

    Raises:
        ValueError: If sun never rises/sets on this date at this location.
    """
    tz = pytz.timezone(timezone)
    location = LocationInfo(
        name="location",
        region="",
        timezone=timezone,
        latitude=lat,
        longitude=lng,
    )
    try:
        s = sun(location.observer, date=activity_date, tzinfo=tz)
    except Exception as exc:
        raise ValueError(
            f"Cannot compute sunrise/sunset for lat={lat}, lng={lng} "
            f"on {activity_date}: {exc}"
        ) from exc

    sunrise: datetime = s["sunrise"]
    sunset: datetime = s["sunset"]
    return sunrise, sunset


def _compute_inauspicious_window(
    sunrise: datetime,
    day_duration: timedelta,
    part_index: int,  # 1-based part number from the constants table
) -> Tuple[datetime, datetime]:
    """
    Compute start/end of an inauspicious window.

    The day (sunrise→sunset) is divided into INAUSPICIOUS_PERIOD_PARTS equal parts.
    The window occupies one such part, identified by its 1-based part_index.

    Args:
        sunrise:      Timezone-aware sunrise datetime.
        day_duration: Total daylight duration.
        part_index:   Which part of the day this window occupies (1-based).
    """
    part_duration = day_duration / INAUSPICIOUS_PERIOD_PARTS
    start = sunrise + (part_index - 1) * part_duration
    end = start + part_duration
    return start, end


def get_day_boundaries(
    lat: float,
    lng: float,
    activity_date: date,
    timezone: str,
) -> dict:
    """
    Compute sunrise, sunset, and all three inauspicious periods.

    Returns a dict with keys:
      sunrise, sunset,
      rahu_start, rahu_end,
      yamaganda_start, yamaganda_end,
      gulika_start, gulika_end

    All values are timezone-aware datetime objects.
    """
    sunrise, sunset = get_sunrise_sunset(lat, lng, activity_date, timezone)
    day_duration = sunset - sunrise

    # Python's datetime.weekday(): Monday=0, Sunday=6
    weekday = activity_date.weekday()

    rahu_start, rahu_end = _compute_inauspicious_window(
        sunrise, day_duration, RAHU_KALAM_PARTS[weekday]
    )
    yamaganda_start, yamaganda_end = _compute_inauspicious_window(
        sunrise, day_duration, YAMAGANDA_PARTS[weekday]
    )
    gulika_start, gulika_end = _compute_inauspicious_window(
        sunrise, day_duration, GULIKA_KALAM_PARTS[weekday]
    )

    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "rahu_start": rahu_start,
        "rahu_end": rahu_end,
        "yamaganda_start": yamaganda_start,
        "yamaganda_end": yamaganda_end,
        "gulika_start": gulika_start,
        "gulika_end": gulika_end,
    }
