"""
slot_engine.py
==============
Generates candidate 15-minute time slots from sunrise to sunset,
computing full Panchang for each slot's midpoint.

Design:
  - Each slot = [start, start + 15min)
  - Panchang evaluated at midpoint (start + 7.5min)
  - Returns List[SlotPanchang] with is_accepted=True (filtering happens separately)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from app.astronomy import datetime_to_jd
from app.constants import SLOT_DURATION_MINUTES
from app.models import SlotPanchang
from app.panchang import compute_full_panchang


_HALF_SLOT = timedelta(minutes=SLOT_DURATION_MINUTES / 2)
_SLOT_DELTA = timedelta(minutes=SLOT_DURATION_MINUTES)


def generate_slots(
    sunrise: datetime,
    end_time: datetime,
    nakshatra_at_birth: int,
) -> List[SlotPanchang]:
    """
    Generate all 15-minute candidate slots between sunrise and end_time.

    Args:
        sunrise:             Timezone-aware sunrise datetime.
        end_time:            Timezone-aware end datetime (e.g. next sunrise).
        nakshatra_at_birth:  0-based birth Nakshatra index for Tarabalam.

    Returns:
        List of SlotPanchang objects (all with is_accepted=True initially).
    """
    slots: List[SlotPanchang] = []
    slot_start = sunrise

    while slot_start + _SLOT_DELTA <= end_time:
        slot_end = slot_start + _SLOT_DELTA
        midpoint = slot_start + _HALF_SLOT

        jd_mid = datetime_to_jd(midpoint)

        (
            nak_idx, nak_name,
            tit_idx, tit_name,
            yog_idx, yog_name,
            kar_idx, kar_name,
            tara_num, tara_name,
        ) = compute_full_panchang(jd_mid, nakshatra_at_birth)

        slots.append(
            SlotPanchang(
                slot_start_iso=slot_start.isoformat(),
                slot_end_iso=slot_end.isoformat(),
                nakshatra_index=nak_idx,
                nakshatra_name=nak_name,
                tithi_index=tit_idx,
                tithi_name=tit_name,
                yoga_index=yog_idx,
                yoga_name=yog_name,
                karana_index=kar_idx,
                karana_name=kar_name,
                tara_number=tara_num,
                tara_name=tara_name,
                is_accepted=True,
                rejection_reasons=[],
            )
        )

        slot_start = slot_end

    return slots
