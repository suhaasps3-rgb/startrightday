"""
predictor.py
============
Orchestrates the full recommendation pipeline.

This module contains ZERO domain logic — it only coordinates the
sequence of calls across other modules. If the pipeline shape changes,
only this file changes.

Pipeline:
  1. Geocode birth_place → lat, lng, timezone
  2. Compute birth Nakshatra at birth_date + birth_time
  3. Compute day boundaries (sunrise, inauspicious windows) for activity_date
  4. Generate 15-min candidate slots (sunrise → sunset)
  5. Apply all rejection filters
  6. Merge contiguous accepted slots into intervals
  7. Map intervals to recommended activities
  8. Build and return RecommendationResponse
"""

from __future__ import annotations

from datetime import date, datetime, time
import pytz

from app.astronomy import datetime_to_jd, get_moon_longitude
from app.filters import apply_all_filters, get_accepted_slots
from app.location import geocode_place
from app.merger import merge_accepted_slots
from app.models import (
    PanchangDetail,
    RecommendationRequest,
    RecommendationResponse,
    TimeInterval,
)
from app.panchang import compute_nakshatra_index
from app.slot_engine import generate_slots
from app.sunrise import get_day_boundaries
from app.timeline import get_activities_for_interval


def _format_time(dt: datetime) -> str:
    """
    Cross-platform 12-hour time formatting without leading zero.
    Works on Windows (no %-I support) and Unix alike.
    """
    hour = dt.hour % 12 or 12   # Convert 0→12, keep 1-11 as-is
    minute = dt.strftime("%M")
    period = "AM" if dt.hour < 12 else "PM"
    return f"{hour}:{minute} {period}"


async def generate_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Full recommendation pipeline for a single request.

    Args:
        request: Validated RecommendationRequest from the API layer.

    Returns:
        RecommendationResponse with status, intervals, and activity tags.
    """

    # ------------------------------------------------------------------
    # Step 1: Geocode birth place
    # ------------------------------------------------------------------
    geo = await geocode_place(request.birth_place)
    tz = pytz.timezone(geo.timezone)

    # ------------------------------------------------------------------
    # Step 2: Compute birth Nakshatra
    # ------------------------------------------------------------------
    birth_dt_naive = datetime.combine(request.birth_date, request.birth_time)
    birth_dt_aware = tz.localize(birth_dt_naive)
    birth_jd = datetime_to_jd(birth_dt_aware)
    birth_moon_lon = get_moon_longitude(birth_jd)
    birth_nakshatra_idx = compute_nakshatra_index(birth_moon_lon)

    # Import here to avoid circular dependency
    from app.constants import NAKSHATRA_NAMES
    birth_nakshatra_name = NAKSHATRA_NAMES[birth_nakshatra_idx]

    # ------------------------------------------------------------------
    # Step 3: Compute day boundaries for activity date
    # ------------------------------------------------------------------
    day = get_day_boundaries(
        lat=geo.latitude,
        lng=geo.longitude,
        activity_date=request.activity_date,
        timezone=geo.timezone,
    )

    # ------------------------------------------------------------------
    # Step 4: Generate candidate slots
    # ------------------------------------------------------------------
    slots = generate_slots(
        sunrise=day["sunrise"],
        sunset=day["sunset"],
        nakshatra_at_birth=birth_nakshatra_idx,
    )

    # ------------------------------------------------------------------
    # Step 5: Apply all filters
    # ------------------------------------------------------------------
    apply_all_filters(slots, day)
    accepted = get_accepted_slots(slots)

    # ------------------------------------------------------------------
    # Step 6: Merge contiguous slots into intervals
    # ------------------------------------------------------------------
    intervals = merge_accepted_slots(accepted)

    # ------------------------------------------------------------------
    # Step 7 + 8: Build response
    # ------------------------------------------------------------------
    if not intervals:
        return RecommendationResponse(
            status="avoid",
            intervals=[],
            message="No auspicious time found today. Consider choosing a different date.",
            birth_nakshatra=birth_nakshatra_name,
            activity_date_display=request.activity_date.strftime("%A, %d %B %Y"),
        )

    time_intervals: list[TimeInterval] = []
    for iv in intervals:
        activities = get_activities_for_interval(iv)
        time_intervals.append(
            TimeInterval(
                start_time=_format_time(iv.start),
                end_time=_format_time(iv.end),
                panchang=PanchangDetail(
                    tara=iv.tara_name,
                    tithi=iv.tithi_name,
                    yoga=iv.yoga_name,
                    karana=iv.karana_name,
                    nakshatra=iv.nakshatra_name,
                ),
                activities=activities,
            )
        )

    return RecommendationResponse(
        status="auspicious",
        intervals=time_intervals,
        message=None,
        birth_nakshatra=birth_nakshatra_name,
        activity_date_display=request.activity_date.strftime("%A, %d %B %Y"),
    )
