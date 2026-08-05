"""
merger.py
=========
Merges contiguous accepted slots into human-readable time intervals.

Two slots are contiguous if:
  slot_a.slot_end_iso == slot_b.slot_start_iso

The representative Panchang for each merged interval is taken from
the MIDPOINT slot of the interval (most representative sample).
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from app.models import SlotPanchang


class MergedInterval:
    """
    A contiguous block of accepted time slots.

    Attributes:
        start:    Start of the first slot in the block.
        end:      End of the last slot in the block.
        slots:    All SlotPanchang objects in this interval (for inspection).
        midpoint_slot: The slot at (or nearest to) the midpoint — used for
                       representative Panchang display.
    """

    def __init__(self, slots: List[SlotPanchang]) -> None:
        if not slots:
            raise ValueError("MergedInterval requires at least one slot.")
        self.slots = slots
        self.start: datetime = datetime.fromisoformat(slots[0].slot_start_iso)
        self.end: datetime = datetime.fromisoformat(slots[-1].slot_end_iso)
        mid_idx = len(slots) // 2
        self.midpoint_slot: SlotPanchang = slots[mid_idx]

    @property
    def tara_name(self) -> str:
        return self.midpoint_slot.tara_name

    @property
    def tara_number(self) -> int:
        return self.midpoint_slot.tara_number

    @property
    def tithi_name(self) -> str:
        return self.midpoint_slot.tithi_name

    @property
    def yoga_name(self) -> str:
        return self.midpoint_slot.yoga_name

    @property
    def karana_name(self) -> str:
        return self.midpoint_slot.karana_name

    @property
    def nakshatra_name(self) -> str:
        return self.midpoint_slot.nakshatra_name

    def __repr__(self) -> str:
        return (
            f"MergedInterval({self.start.strftime('%H:%M')} – "
            f"{self.end.strftime('%H:%M')}, {len(self.slots)} slots)"
        )


def merge_accepted_slots(accepted_slots: List[SlotPanchang]) -> List[MergedInterval]:
    """
    Merge contiguous accepted slots into intervals.

    Args:
        accepted_slots: Slots that have passed all filters (is_accepted=True).

    Returns:
        List of MergedInterval, sorted by start time.
    """
    if not accepted_slots:
        return []

    intervals: List[MergedInterval] = []
    current_group: List[SlotPanchang] = [accepted_slots[0]]

    for slot in accepted_slots[1:]:
        prev_end = current_group[-1].slot_end_iso
        if slot.slot_start_iso == prev_end:
            # Contiguous — extend current group
            current_group.append(slot)
        else:
            # Gap detected — close current interval, start new one
            intervals.append(MergedInterval(current_group))
            current_group = [slot]

    # Close the final group
    intervals.append(MergedInterval(current_group))

    return intervals
