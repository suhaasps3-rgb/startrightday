"""
panchang.py
===========
Computes the five classical Panchang elements from astronomical positions.

All functions are pure: given Moon/Sun longitudes, they return deterministic values.
No side effects. All formulas derived from classical Vedic astronomy.

Elements computed:
  1. Nakshatra  — lunar mansion of the Moon
  2. Tithi      — lunar day (Moon-Sun elongation)
  3. Yoga       — luni-solar sum division
  4. Karana     — half-tithi
  5. Tarabalam  — natal Nakshatra distance (Tara type 1-9)
"""

from __future__ import annotations

import math
from typing import Tuple

from app.constants import (
    BAD_TITHIS,
    KARANA_NAMES,
    NAKSHATRA_NAMES,
    NAKSHATRA_SPAN_DEG,
    TITHI_NAMES,
    TITHI_SPAN_DEG,
    TOTAL_NAKSHATRAS,
    YOGA_NAMES,
    YOGA_SPAN_DEG,
    TARA_NAMES,
)
from app.astronomy import get_moon_sun_longitudes, datetime_to_jd


# ---------------------------------------------------------------------------
# Nakshatra
# ---------------------------------------------------------------------------

def compute_nakshatra_index(moon_lon: float) -> int:
    """
    Return 0-based Nakshatra index (0=Ashwini … 26=Revati).

    Formula: floor(moon_lon / (360 / 27))
    """
    return int(moon_lon / NAKSHATRA_SPAN_DEG) % TOTAL_NAKSHATRAS


def compute_nakshatra_name(moon_lon: float) -> str:
    return NAKSHATRA_NAMES[compute_nakshatra_index(moon_lon)]


# ---------------------------------------------------------------------------
# Tithi
# ---------------------------------------------------------------------------

def compute_tithi_index(moon_lon: float, sun_lon: float) -> int:
    """
    Return 0-based Tithi index (0=Pratipada … 29=Amavasya).

    Formula: floor(((moon_lon - sun_lon) % 360) / 12)
    The modulo ensures we handle cases where moon is behind sun.
    """
    elongation = (moon_lon - sun_lon) % 360.0
    return int(elongation / TITHI_SPAN_DEG) % 30


def compute_tithi_name(moon_lon: float, sun_lon: float) -> str:
    return TITHI_NAMES[compute_tithi_index(moon_lon, sun_lon)]


# ---------------------------------------------------------------------------
# Yoga
# ---------------------------------------------------------------------------

def compute_yoga_index(moon_lon: float, sun_lon: float) -> int:
    """
    Return 0-based Yoga index (0=Vishkambha … 26=Vaidhriti).

    Formula: floor(((moon_lon + sun_lon) % 360) / (360/27))
    """
    combined = (moon_lon + sun_lon) % 360.0
    return int(combined / YOGA_SPAN_DEG) % 27


def compute_yoga_name(moon_lon: float, sun_lon: float) -> str:
    return YOGA_NAMES[compute_yoga_index(moon_lon, sun_lon)]


# ---------------------------------------------------------------------------
# Karana
# ---------------------------------------------------------------------------

def compute_karana_index(moon_lon: float, sun_lon: float) -> int:
    """
    Return 0-based Karana index (0–10) mapping to KARANA_NAMES.

    There are 60 Karanas in a lunar month:
      - Karana 1 (Kimstughna) is fixed at the very start.
      - Karanas 2–57 cycle through the 7 movable Karanas (Bava…Vishti) 8 times.
      - Karanas 58–60 are fixed (Shakuni, Chatushpada, Naga).

    This mapping is standard classical Vedic computation.
    """
    elongation = (moon_lon - sun_lon) % 360.0
    # Each Karana spans 6° (half of 12° Tithi)
    karana_number = int(elongation / 6.0)  # 0–59

    if karana_number == 0:
        return 10  # Kimstughna (fixed, first)
    elif karana_number <= 56:
        return (karana_number - 1) % 7  # Cycles through Bava(0)…Vishti(6)
    elif karana_number == 57:
        return 7   # Shakuni (fixed)
    elif karana_number == 58:
        return 8   # Chatushpada (fixed)
    else:
        return 9   # Naga (fixed)


def compute_karana_name(moon_lon: float, sun_lon: float) -> str:
    return KARANA_NAMES[compute_karana_index(moon_lon, sun_lon)]


# ---------------------------------------------------------------------------
# Tarabalam
# ---------------------------------------------------------------------------

def compute_tara_number(
    nakshatra_at_slot: int,
    nakshatra_at_birth: int,
) -> int:
    """
    Compute Tara number (1–9) for a given slot relative to birth Nakshatra.

    Formula:
      distance = ((nakshatra_at_slot - nakshatra_at_birth) % 27) + 1
      tara_number = ((distance - 1) % 9) + 1
    """
    distance = ((nakshatra_at_slot - nakshatra_at_birth) % TOTAL_NAKSHATRAS) + 1
    tara_number = ((distance - 1) % 9) + 1
    return tara_number


def compute_tara_name(nakshatra_at_slot: int, nakshatra_at_birth: int) -> str:
    tara_num = compute_tara_number(nakshatra_at_slot, nakshatra_at_birth)
    return TARA_NAMES[tara_num]


# ---------------------------------------------------------------------------
# Full Panchang at a Julian Day
# ---------------------------------------------------------------------------

def compute_full_panchang(
    jd_ut: float,
    nakshatra_at_birth: int,
) -> Tuple[int, str, int, str, int, str, int, str, int, str]:
    """
    Compute all five Panchang elements for a given Julian Day.

    Args:
        jd_ut:              Julian Day (UT) of the slot midpoint.
        nakshatra_at_birth: 0-based Nakshatra index at the native's birth.

    Returns:
        Tuple of (nakshatra_idx, nakshatra_name,
                  tithi_idx, tithi_name,
                  yoga_idx, yoga_name,
                  karana_idx, karana_name,
                  tara_num, tara_name)
    """
    moon_lon, sun_lon = get_moon_sun_longitudes(jd_ut)

    nak_idx = compute_nakshatra_index(moon_lon)
    nak_name = NAKSHATRA_NAMES[nak_idx]

    tit_idx = compute_tithi_index(moon_lon, sun_lon)
    tit_name = TITHI_NAMES[tit_idx]

    yog_idx = compute_yoga_index(moon_lon, sun_lon)
    yog_name = YOGA_NAMES[yog_idx]

    kar_idx = compute_karana_index(moon_lon, sun_lon)
    kar_name = KARANA_NAMES[kar_idx]

    tara_num = compute_tara_number(nak_idx, nakshatra_at_birth)
    tara_name = TARA_NAMES[tara_num]

    return (
        nak_idx, nak_name,
        tit_idx, tit_name,
        yog_idx, yog_name,
        kar_idx, kar_name,
        tara_num, tara_name,
    )
