"""
transitions.py
==============
Detects when Panchang elements change across a day.

This module is a utility used by slot_engine.py to annotate
where transitions in Nakshatra, Tithi, Yoga, or Karana occur.
Not required for the current slot-based approach, but included
for future use (e.g., computing exact transition times for
Abhijit Muhurta, Amrita Kalam, Varjyam).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from app.astronomy import datetime_to_jd, get_moon_sun_longitudes
from app.panchang import (
    compute_nakshatra_index,
    compute_tithi_index,
    compute_yoga_index,
    compute_karana_index,
)


def find_nakshatra_transitions(
    start: datetime,
    end: datetime,
    resolution_minutes: int = 15,
) -> List[Tuple[datetime, int]]:
    """
    Return a list of (transition_time, new_nakshatra_index) tuples
    where the Moon's Nakshatra changes between start and end.

    Args:
        start:              Timezone-aware start datetime.
        end:                Timezone-aware end datetime.
        resolution_minutes: Sampling resolution (default 15 min).

    Returns:
        List of (datetime, nakshatra_index) at each detected transition.
    """
    transitions: List[Tuple[datetime, int]] = []
    current = start
    delta = timedelta(minutes=resolution_minutes)

    jd_prev = datetime_to_jd(current)
    moon_lon, _ = get_moon_sun_longitudes(jd_prev)
    prev_nak = compute_nakshatra_index(moon_lon)

    current += delta
    while current <= end:
        jd = datetime_to_jd(current)
        moon_lon, _ = get_moon_sun_longitudes(jd)
        nak = compute_nakshatra_index(moon_lon)
        if nak != prev_nak:
            transitions.append((current, nak))
            prev_nak = nak
        current += delta

    return transitions


def find_tithi_transitions(
    start: datetime,
    end: datetime,
    resolution_minutes: int = 15,
) -> List[Tuple[datetime, int]]:
    """
    Return (transition_time, new_tithi_index) tuples where Tithi changes.
    """
    transitions: List[Tuple[datetime, int]] = []
    current = start
    delta = timedelta(minutes=resolution_minutes)

    jd_prev = datetime_to_jd(current)
    moon_lon, sun_lon = get_moon_sun_longitudes(jd_prev)
    prev_tithi = compute_tithi_index(moon_lon, sun_lon)

    current += delta
    while current <= end:
        jd = datetime_to_jd(current)
        moon_lon, sun_lon = get_moon_sun_longitudes(jd)
        tithi = compute_tithi_index(moon_lon, sun_lon)
        if tithi != prev_tithi:
            transitions.append((current, tithi))
            prev_tithi = tithi
        current += delta

    return transitions
