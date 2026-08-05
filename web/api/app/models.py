"""
models.py
=========
Pydantic v2 request/response models for the StartRightDay API.
All validation happens here — predictor.py trusts these types completely.
"""

from __future__ import annotations

from datetime import date, time
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class RecommendationRequest(BaseModel):
    """
    Input from the Flutter frontend.
    birth_place is a human-readable city/town name resolved via OSM geocoding.
    """

    birth_place: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City or town name of birth place (e.g., 'Mumbai', 'New Delhi')",
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Date of birth in ISO format (YYYY-MM-DD)",
    )
    birth_time: Optional[time] = Field(
        default=None,
        description="Time of birth in HH:MM (24-hour format)",
    )
    known_nakshatra: Optional[str] = Field(
        default=None,
        description="Optional pre-known birth nakshatra to skip birth panchang calculation",
    )
    activity_date: date = Field(
        ...,
        description="Date for which to find auspicious intervals (YYYY-MM-DD)",
    )
    lat: Optional[float] = Field(
        default=None,
        description="Latitude of the birth place (optional if geocoding fallback is used)",
    )
    lon: Optional[float] = Field(
        default=None,
        description="Longitude of the birth place (optional if geocoding fallback is used)",
    )

    @field_validator("birth_place")
    @classmethod
    def strip_birth_place(cls, v: str) -> str:
        return v.strip()


# ---------------------------------------------------------------------------
# Sub-models for response
# ---------------------------------------------------------------------------

class PanchangDetail(BaseModel):
    """Panchang elements at the representative midpoint of a time interval."""

    tara: str = Field(..., description="Tarabalam name (e.g., 'Sampat', 'Kshema')")
    tithi: str = Field(..., description="Tithi name (e.g., 'Tritiya', 'Panchami')")
    yoga: str = Field(..., description="Yoga name (e.g., 'Siddhi', 'Shubha')")
    karana: str = Field(..., description="Karana name (e.g., 'Bava', 'Balava')")
    nakshatra: str = Field(..., description="Nakshatra name at interval midpoint")


class TimeInterval(BaseModel):
    """A single contiguous auspicious time window."""

    start_time: str = Field(
        ...,
        description="Start time formatted as '10:45 AM'",
    )
    end_time: str = Field(
        ...,
        description="End time formatted as '12:15 PM'",
    )
    panchang: PanchangDetail
    activities: List[str] = Field(
        default_factory=list,
        description="Recommended activity categories for this interval",
    )


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class RecommendationResponse(BaseModel):
    """
    Full recommendation output returned to Flutter.
    status='auspicious' → one or more intervals present.
    status='avoid'      → no intervals found.
    """

    status: Literal["auspicious", "avoid"]
    intervals: List[TimeInterval] = Field(default_factory=list)
    message: Optional[str] = Field(
        default=None,
        description="Human-readable message (populated when status='avoid')",
    )
    # Metadata included for transparency / future debug panel
    birth_nakshatra: Optional[str] = Field(
        default=None,
        description="Nakshatra of the native at birth time",
    )
    activity_date_display: Optional[str] = Field(
        default=None,
        description="Activity date formatted for display (e.g., 'Wednesday, 5 August 2026')",
    )


# ---------------------------------------------------------------------------
# Internal-use types (not part of the public API response)
# ---------------------------------------------------------------------------

class GeoLocation(BaseModel):
    """Resolved geocoding result."""

    place_name: str
    latitude: float
    longitude: float
    timezone: str  # IANA timezone string, e.g. "Asia/Kolkata"


class DayBoundaries(BaseModel):
    """Sunrise/sunset and inauspicious windows for a given day."""

    sunrise_iso: str   # ISO 8601 datetime string (timezone-aware)
    sunset_iso: str
    rahu_start_iso: str
    rahu_end_iso: str
    yamaganda_start_iso: str
    yamaganda_end_iso: str
    gulika_start_iso: str
    gulika_end_iso: str


class SlotPanchang(BaseModel):
    """Computed Panchang elements for a 15-minute slot."""

    slot_start_iso: str
    slot_end_iso: str
    nakshatra_index: int
    nakshatra_name: str
    tithi_index: int
    tithi_name: str
    yoga_index: int
    yoga_name: str
    karana_index: int
    karana_name: str
    tara_number: int      # 1–9
    tara_name: str
    is_accepted: bool = True  # set to False by filters
    rejection_reasons: List[str] = Field(default_factory=list)
