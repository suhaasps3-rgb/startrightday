"""
sweep_test.py
=============
Scans 14 consecutive dates and prints:
  - Status (AUSPICIOUS / AVOID)
  - Number of intervals
  - Rejection reasons summary
  - All accepted windows with full Panchang

Run from backend/ directory:
    python sweep_test.py
"""

import asyncio
import sys
from datetime import date, time, datetime, timedelta

sys.path.insert(0, '.')

from app.location import geocode_place
from app.astronomy import datetime_to_jd, get_moon_longitude
from app.panchang import compute_nakshatra_index
from app.sunrise import get_day_boundaries
from app.slot_engine import generate_slots
from app.filters import apply_all_filters
from app.merger import merge_accepted_slots
from app.timeline import get_activities_for_interval
from app.constants import NAKSHATRA_NAMES
import pytz


# ---------------------------------------------------------------------------
# Config — change these to test different people/places
# ---------------------------------------------------------------------------
BIRTH_PLACE   = "Mumbai, India"
BIRTH_DATE    = date(1990, 6, 15)
BIRTH_TIME    = time(8, 30)
START_DATE    = date(2026, 8, 5)
DAYS_TO_SCAN  = 14
# ---------------------------------------------------------------------------


def fmt_time(dt: datetime) -> str:
    h = dt.hour % 12 or 12
    return f"{h}:{dt.strftime('%M')} {'AM' if dt.hour < 12 else 'PM'}"


async def main():
    print()
    print("=" * 70)
    print("  StartRightDay - Multi-Date Sweep Test")
    print(f"  Birth: {BIRTH_PLACE}  |  {BIRTH_DATE}  |  {BIRTH_TIME}")
    print(f"  Scanning {DAYS_TO_SCAN} days from {START_DATE}")
    print("=" * 70)

    # Geocode once
    geo = await geocode_place(BIRTH_PLACE)
    tz  = pytz.timezone(geo.timezone)
    print(f"\n  Geocoded: lat={geo.latitude:.4f}, lng={geo.longitude:.4f}, tz={geo.timezone}")

    # Birth Nakshatra once
    birth_dt  = tz.localize(datetime.combine(BIRTH_DATE, BIRTH_TIME))
    birth_jd  = datetime_to_jd(birth_dt)
    birth_nak = compute_nakshatra_index(get_moon_longitude(birth_jd))
    print(f"  Birth Nakshatra: {NAKSHATRA_NAMES[birth_nak]} (index {birth_nak})\n")

    summary_rows = []

    for i in range(DAYS_TO_SCAN):
        activity_date = START_DATE + timedelta(days=i)

        # Day boundaries
        day = get_day_boundaries(geo.latitude, geo.longitude, activity_date, geo.timezone)

        # Slots -> filter -> merge
        slots = generate_slots(day['sunrise'], day['sunset'], birth_nak)
        apply_all_filters(slots, day)
        accepted  = [s for s in slots if s.is_accepted]
        rejected  = [s for s in slots if not s.is_accepted]
        intervals = merge_accepted_slots(accepted)

        # Rejection summary
        reason_counts: dict[str, int] = {}
        for slot in rejected:
            for r in slot.rejection_reasons:
                reason_counts[r] = reason_counts.get(r, 0) + 1
        top_reason = max(reason_counts, key=reason_counts.get) if reason_counts else "-"

        status = "AUSPICIOUS" if intervals else "AVOID     "
        day_name = activity_date.strftime("%a %d %b")

        summary_rows.append((activity_date, status, len(slots), len(accepted), len(intervals), top_reason, intervals, day, slots))

        print(f"  [{status}] {day_name}  |  {len(accepted):>2}/{len(slots)} slots accepted  |  {len(intervals)} interval(s)  |  Top rejection: {top_reason}")

    # ---------------------------------------------------------------------------
    # Detailed breakdown per AUSPICIOUS day
    # ---------------------------------------------------------------------------
    print()
    print("=" * 70)
    print("  DETAILED: Auspicious Days")
    print("=" * 70)

    auspicious_days = [(r[0], r[6], r[7]) for r in summary_rows if r[1].strip() == "AUSPICIOUS"]

    if not auspicious_days:
        print("\n  No auspicious days found in this range.\n")
    else:
        for act_date, intervals, day in auspicious_days:
            print(f"\n  {act_date.strftime('%A, %d %B %Y')}")
            print(f"  Sunrise {fmt_time(day['sunrise'])}  |  Sunset {fmt_time(day['sunset'])}")
            print(f"  Rahu {fmt_time(day['rahu_start'])}-{fmt_time(day['rahu_end'])}  "
                  f"Yamaganda {fmt_time(day['yamaganda_start'])}-{fmt_time(day['yamaganda_end'])}  "
                  f"Gulika {fmt_time(day['gulika_start'])}-{fmt_time(day['gulika_end'])}")
            print(f"  {'-'*66}")
            for idx, iv in enumerate(intervals, 1):
                activities = get_activities_for_interval(iv)
                dur = int((iv.end - iv.start).total_seconds() / 60)
                print(f"\n  Window {idx}: {fmt_time(iv.start)} - {fmt_time(iv.end)}  ({dur} min)")
                print(f"    Nakshatra : {iv.nakshatra_name}")
                print(f"    Tara      : {iv.tara_name}")
                print(f"    Tithi     : {iv.tithi_name}")
                print(f"    Yoga      : {iv.yoga_name}")
                print(f"    Karana    : {iv.karana_name}")
                print(f"    Good for  : {', '.join(activities[:5])}")

    # ---------------------------------------------------------------------------
    # Detailed breakdown per AVOID day
    # ---------------------------------------------------------------------------
    print()
    print("=" * 70)
    print("  DETAILED: Avoid Days - Why Each Day Failed")
    print("=" * 70)

    avoid_days = [(r[0], r[7], r[8]) for r in summary_rows if r[1].strip() == "AVOID"]

    for act_date, day, slots in avoid_days:
        reason_counts: dict[str, int] = {}
        for slot in slots:
            for r in slot.rejection_reasons:
                reason_counts[r] = reason_counts.get(r, 0) + 1

        print(f"\n  {act_date.strftime('%A, %d %B %Y')}")
        for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
            pct = int(count / len(slots) * 100)
            bar = '#' * (pct // 5)
            print(f"    {reason:<42} {bar:<20} {pct:>3}% of day")

    print()
    print("=" * 70)
    print(f"  SUMMARY: {len(auspicious_days)} auspicious / {len(avoid_days)} avoid out of {DAYS_TO_SCAN} days")
    print("=" * 70)
    print()


asyncio.run(main())
