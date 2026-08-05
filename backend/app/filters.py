"""
filters.py
==========
Applies all rejection rules to a list of SlotPanchang objects.

Architecture:
  - Each filter is a standalone function: (slot, context) → bool (True = reject)
  - apply_all_filters() runs them all in sequence and records reasons
  - New rules (Durmuhurta, Varjyam, etc.) = add one function + register it

This makes the rule engine individually testable and fully auditable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from app.constants import BAD_KARANAS, BAD_TARAS, BAD_TITHIS, BAD_YOGAS
from app.models import SlotPanchang


# ---------------------------------------------------------------------------
# Individual rejection rules
# Each returns (should_reject: bool, reason: str)
# ---------------------------------------------------------------------------

def _reject_bad_tara(slot: SlotPanchang, _ctx: Dict) -> Tuple[bool, str]:
    if slot.tara_number in BAD_TARAS:
        return True, f"Tara: {slot.tara_name} (inauspicious)"
    return False, ""


def _reject_bad_tithi(slot: SlotPanchang, _ctx: Dict) -> Tuple[bool, str]:
    if slot.tithi_index in BAD_TITHIS:
        return True, f"Tithi: {slot.tithi_name} (inauspicious)"
    return False, ""


def _reject_bad_yoga(slot: SlotPanchang, _ctx: Dict) -> Tuple[bool, str]:
    if slot.yoga_index in BAD_YOGAS:
        return True, f"Yoga: {slot.yoga_name} (inauspicious)"
    return False, ""


def _reject_bad_karana(slot: SlotPanchang, _ctx: Dict) -> Tuple[bool, str]:
    if slot.karana_index in BAD_KARANAS:
        return True, f"Karana: {slot.karana_name} (Bhadra/inauspicious)"
    return False, ""


def _reject_rahu_kalam(slot: SlotPanchang, ctx: Dict) -> Tuple[bool, str]:
    """Reject if slot overlaps Rahu Kalam (any overlap = reject)."""
    slot_start: datetime = datetime.fromisoformat(slot.slot_start_iso)
    slot_end: datetime = datetime.fromisoformat(slot.slot_end_iso)
    rahu_start: datetime = ctx["rahu_start"]
    rahu_end: datetime = ctx["rahu_end"]
    if slot_start < rahu_end and slot_end > rahu_start:
        return True, "Rahu Kalam"
    return False, ""


def _reject_yamaganda(slot: SlotPanchang, ctx: Dict) -> Tuple[bool, str]:
    """Reject if slot overlaps Yamaganda."""
    slot_start = datetime.fromisoformat(slot.slot_start_iso)
    slot_end = datetime.fromisoformat(slot.slot_end_iso)
    ya_start: datetime = ctx["yamaganda_start"]
    ya_end: datetime = ctx["yamaganda_end"]
    if slot_start < ya_end and slot_end > ya_start:
        return True, "Yamaganda"
    return False, ""


def _reject_gulika_kalam(slot: SlotPanchang, ctx: Dict) -> Tuple[bool, str]:
    """Reject if slot overlaps Gulika Kalam."""
    slot_start = datetime.fromisoformat(slot.slot_start_iso)
    slot_end = datetime.fromisoformat(slot.slot_end_iso)
    gu_start: datetime = ctx["gulika_start"]
    gu_end: datetime = ctx["gulika_end"]
    if slot_start < gu_end and slot_end > gu_start:
        return True, "Gulika Kalam"
    return False, ""


# ---------------------------------------------------------------------------
# Filter registry — ORDER MATTERS (fastest/most-rejecting filters first)
# ---------------------------------------------------------------------------
_FILTERS = [
    _reject_rahu_kalam,     # Time-based, rejects entire blocks quickly
    _reject_yamaganda,
    _reject_gulika_kalam,
    _reject_bad_tara,       # Most common rejection
    _reject_bad_tithi,
    _reject_bad_yoga,
    _reject_bad_karana,
]


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def apply_all_filters(
    slots: List[SlotPanchang],
    day_boundaries: Dict,
) -> List[SlotPanchang]:
    """
    Apply all rejection rules to each slot.

    Mutates each SlotPanchang's is_accepted and rejection_reasons fields.
    Returns the same list (with some slots now marked is_accepted=False).

    Args:
        slots:          List of SlotPanchang from slot_engine.generate_slots().
        day_boundaries: Dict from sunrise.get_day_boundaries() with rahu_start,
                        rahu_end, yamaganda_start, yamaganda_end, etc.
    """
    for slot in slots:
        for rule_fn in _FILTERS:
            should_reject, reason = rule_fn(slot, day_boundaries)
            if should_reject:
                slot.is_accepted = False
                slot.rejection_reasons.append(reason)
                # Do NOT break — collect all rejection reasons for transparency

    return slots


def get_accepted_slots(slots: List[SlotPanchang]) -> List[SlotPanchang]:
    """Return only the slots that passed all filters."""
    return [s for s in slots if s.is_accepted]
