"""
timeline.py
===========
Maps auspicious intervals to recommended activity categories.

Logic:
  - Primary source: Tara type → base activity list
  - Secondary refinement: Tithi type adds/removes categories
  - Output: deduplicated, sorted list of activity strings per interval

This is deterministic and rule-based. No scoring or ranking.
"""

from __future__ import annotations

from typing import List

from app.constants import TARA_ACTIVITY_MAP
from app.merger import MergedInterval


# Tithi-based activity refinements
# Tithi index ranges: Shukla 0-14, Krishna 15-29
# Jaya tithis (3, 8, 13, 18, 23, 28 — 0-indexed): good for competitive/career
# Purna tithis (4, 14, 19, 29 — 0-indexed Purnima/Amavasya adjacent): completions
# Nanda tithis (0, 5, 10, 15, 20, 25): beginnings, prosperity

_JAYA_TITHIS = frozenset({2, 7, 12, 17, 22, 27})   # Tritiya, Saptami, etc.
_PURNA_TITHIS = frozenset({4, 9, 14, 19, 24})       # Panchami, Dashami, etc.
_NANDA_TITHIS = frozenset({0, 5, 10, 15, 20, 25})   # Pratipada, Shashthi, etc.
_BHADRA_TITHIS = frozenset({1, 6, 11, 16, 21, 26})  # Dwitiya, Saptami, etc.

_TITHI_EXTRA_ACTIVITIES = {
    # Jaya: victory, competition, career, exams
    "jaya": ["Exams", "Competitions", "Interviews", "Career Moves"],
    # Purna: completion, abundance
    "purna": ["Housewarming", "Loan Closure", "Project Completion"],
    # Nanda: new beginnings, auspicious starts
    "nanda": ["New Business", "Vehicle Purchase", "Education Enrollment"],
    # Bhadra: stability, relationships
    "bhadra": ["Marriage Discussion", "Partnerships", "Family Decisions"],
}


def _get_tithi_class(tithi_index: int) -> str:
    if tithi_index in _JAYA_TITHIS:
        return "jaya"
    if tithi_index in _PURNA_TITHIS:
        return "purna"
    if tithi_index in _NANDA_TITHIS:
        return "nanda"
    if tithi_index in _BHADRA_TITHIS:
        return "bhadra"
    return "neutral"


def get_activities_for_interval(interval: MergedInterval) -> List[str]:
    """
    Return a deduplicated, sorted list of recommended activities for
    a given auspicious interval.

    Args:
        interval: A MergedInterval from merger.merge_accepted_slots().

    Returns:
        List of activity category strings (e.g., ["Business", "Career", ...]).
    """
    tara_num = interval.tara_number
    tithi_idx = interval.midpoint_slot.tithi_index

    # Base activities from Tara
    base: List[str] = list(TARA_ACTIVITY_MAP.get(tara_num, []))

    # Refinement from Tithi class
    tithi_class = _get_tithi_class(tithi_idx)
    extras: List[str] = _TITHI_EXTRA_ACTIVITIES.get(tithi_class, [])

    # Merge, deduplicate, sort
    combined = list(dict.fromkeys(base + extras))  # preserves order, deduplicates
    return combined
