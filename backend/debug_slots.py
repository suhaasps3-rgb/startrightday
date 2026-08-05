"""
debug_slots.py
==============
Diagnostic script — shows EVERY slot for a given date and exactly
which rules rejected it. Run from the backend/ directory:

    python debug_slots.py
"""

import asyncio
from datetime import date, time, datetime

# Add app to path
import sys
sys.path.insert(0, '.')

from app.location import geocode_place
from app.astronomy import datetime_to_jd, get_moon_longitude
from app.panchang import compute_nakshatra_index
from app.sunrise import get_day_boundaries
from app.slot_engine import generate_slots
from app.filters import apply_all_filters
from app.constants import NAKSHATRA_NAMES
import pytz


async def main():
    # ── Inputs ───────────────────────────────────────────────────────────────
    birth_place   = "Mumbai, India"
    birth_date    = date(1990, 6, 15)
    birth_time    = time(8, 30)
    activity_date = date(2026, 8, 5)   # ← the "bad" date
    # ─────────────────────────────────────────────────────────────────────────

    print(f"\n{'='*62}")
    print(f"  StartRightDay - Slot Diagnostics")
    print(f"  Birth place  : {birth_place}")
    print(f"  Birth date   : {birth_date}  |  Birth time: {birth_time}")
    print(f"  Activity date: {activity_date}")
    print(f"{'='*62}\n")

    # Geocode
    geo = await geocode_place(birth_place)
    tz  = pytz.timezone(geo.timezone)
    print(f"  Location     : lat={geo.latitude:.4f}, lng={geo.longitude:.4f}")
    print(f"  Timezone     : {geo.timezone}\n")

    # Birth Nakshatra
    birth_dt = tz.localize(datetime.combine(birth_date, birth_time))
    birth_jd = datetime_to_jd(birth_dt)
    birth_moon = get_moon_longitude(birth_jd)
    birth_nak  = compute_nakshatra_index(birth_moon)
    print(f"  Birth Nakshatra: {NAKSHATRA_NAMES[birth_nak]} (index {birth_nak})\n")

    # Day boundaries
    day = get_day_boundaries(geo.latitude, geo.longitude, activity_date, geo.timezone)
    print(f"  Sunrise      : {day['sunrise'].strftime('%I:%M %p')}")
    print(f"  Sunset       : {day['sunset'].strftime('%I:%M %p')}")
    print(f"  Rahu Kalam   : {day['rahu_start'].strftime('%I:%M %p')} – {day['rahu_end'].strftime('%I:%M %p')}")
    print(f"  Yamaganda    : {day['yamaganda_start'].strftime('%I:%M %p')} – {day['yamaganda_end'].strftime('%I:%M %p')}")
    print(f"  Gulika Kalam : {day['gulika_start'].strftime('%I:%M %p')} – {day['gulika_end'].strftime('%I:%M %p')}")

    # Generate + filter slots
    slots = generate_slots(day['sunrise'], day['sunset'], birth_nak)
    apply_all_filters(slots, day)

    accepted = [s for s in slots if s.is_accepted]
    rejected = [s for s in slots if not s.is_accepted]

    print(f"\n  Total slots  : {len(slots)}")
    print(f"  Accepted     : {len(accepted)}")
    print(f"  Rejected     : {len(rejected)}")

    # Rejection reason summary
    reason_counts: dict[str, int] = {}
    for slot in rejected:
        for r in slot.rejection_reasons:
            reason_counts[r] = reason_counts.get(r, 0) + 1

    print(f"\n  Rejection Breakdown:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        bar = '#' * min(count, 40)
        print(f"    {reason:<40} {bar} ({count} slots)")

    # Show first 5 rejected slots in detail
    print(f"\n  Sample Rejected Slots (first 5):")
    print(f"  {'Time':<12} {'Nakshatra':<20} {'Tara':<16} {'Tithi':<16} {'Yoga':<16} Reasons")
    print(f"  {'-'*105}")
    for slot in rejected[:5]:
        t = datetime.fromisoformat(slot.slot_start_iso).strftime('%I:%M %p').lstrip('0')
        reasons = ', '.join(slot.rejection_reasons)
        print(f"  {t:<12} {slot.nakshatra_name:<20} {slot.tara_name:<16} {slot.tithi_name:<16} {slot.yoga_name:<16} REJECT: {reasons}")

    if accepted:
        print(f"\n  Accepted Slots:")
        for slot in accepted:
            t = datetime.fromisoformat(slot.slot_start_iso).strftime('%I:%M %p').lstrip('0')
            print(f"  {t} -> Tara={slot.tara_name}, Tithi={slot.tithi_name}, Yoga={slot.yoga_name}")
    else:
        print(f"\n  [X] No slots passed all filters -> status = AVOID")

    print(f"\n{'='*62}\n")


asyncio.run(main())
