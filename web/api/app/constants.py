"""
constants.py
============
All domain-level constants for the Vedic Panchang engine.
No logic here — only named values. Every magic number in the codebase
must be defined and named here.
"""

from typing import Dict, FrozenSet, List, Tuple

# ---------------------------------------------------------------------------
# Nakshatras (27 lunar mansions, in order, 0-indexed)
# ---------------------------------------------------------------------------
NAKSHATRA_NAMES: List[str] = [
    "Ashwini",        # 0
    "Bharani",        # 1
    "Krittika",       # 2
    "Rohini",         # 3
    "Mrigashira",     # 4
    "Ardra",          # 5
    "Punarvasu",      # 6
    "Pushya",         # 7
    "Ashlesha",       # 8
    "Magha",          # 9
    "Purva Phalguni", # 10
    "Uttara Phalguni",# 11
    "Hasta",          # 12
    "Chitra",         # 13
    "Swati",          # 14
    "Vishakha",       # 15
    "Anuradha",       # 16
    "Jyeshtha",       # 17
    "Mula",           # 18
    "Purva Ashadha",  # 19
    "Uttara Ashadha", # 20
    "Shravana",       # 21
    "Dhanishtha",     # 22
    "Shatabhisha",    # 23
    "Purva Bhadrapada",# 24
    "Uttara Bhadrapada",# 25
    "Revati",         # 26
]

TOTAL_NAKSHATRAS: int = 27
NAKSHATRA_SPAN_DEG: float = 360.0 / TOTAL_NAKSHATRAS  # 13.333...°

# ---------------------------------------------------------------------------
# Tithis (30 lunar days, 0-indexed internally, displayed 1-indexed)
# ---------------------------------------------------------------------------
TITHI_NAMES: List[str] = [
    "Pratipada",  # 1
    "Dwitiya",    # 2
    "Tritiya",    # 3
    "Chaturthi",  # 4
    "Panchami",   # 5
    "Shashthi",   # 6
    "Saptami",    # 7
    "Ashtami",    # 8
    "Navami",     # 9
    "Dashami",    # 10
    "Ekadashi",   # 11
    "Dwadashi",   # 12
    "Trayodashi", # 13
    "Chaturdashi",# 14
    "Purnima",    # 15  (Shukla Paksha full moon)
    "Pratipada",  # 16  (Krishna Paksha)
    "Dwitiya",    # 17
    "Tritiya",    # 18
    "Chaturthi",  # 19
    "Panchami",   # 20
    "Shashthi",   # 21
    "Saptami",    # 22
    "Ashtami",    # 23
    "Navami",     # 24
    "Dashami",    # 25
    "Ekadashi",   # 26
    "Dwadashi",   # 27
    "Trayodashi", # 28
    "Chaturdashi",# 29
    "Amavasya",   # 30
]

TITHI_SPAN_DEG: float = 12.0  # Each Tithi = 12° of Moon-Sun elongation

# Tithi classifications (0-indexed)
# Rikta = inauspicious for most activities
RIKTA_TITHIS: FrozenSet[int] = frozenset({3, 7, 11, 18, 22, 26})  # Chaturthi (×2), Ashtami (×2), Dwadashi (×2)

# Absolutely inauspicious Tithis — rejected outright
BAD_TITHIS: FrozenSet[int] = frozenset({
    3,   # Chaturthi (Shukla)
    7,   # Ashtami (Shukla)
    11,  # Dwadashi (Shukla) — debated; included conservatively
    13,  # Chaturdashi (Shukla)
    14,  # Purnima — fine for worship, not for new beginnings in many traditions
    18,  # Chaturthi (Krishna)
    22,  # Ashtami (Krishna)
    26,  # Dwadashi (Krishna)
    28,  # Chaturdashi (Krishna)
    29,  # Amavasya
})

# ---------------------------------------------------------------------------
# Yogas (27 luni-solar yogas, 0-indexed)
# ---------------------------------------------------------------------------
YOGA_NAMES: List[str] = [
    "Vishkambha",  # 0  — inauspicious
    "Priti",       # 1
    "Ayushman",    # 2
    "Saubhagya",   # 3
    "Shobhana",    # 4
    "Atiganda",    # 5  — inauspicious
    "Sukarman",    # 6
    "Dhriti",      # 7
    "Shoola",      # 8  — inauspicious
    "Ganda",       # 9  — inauspicious
    "Vriddhi",     # 10
    "Dhruva",      # 11
    "Vyaghata",    # 12 — inauspicious
    "Harshana",    # 13
    "Vajra",       # 14 — inauspicious
    "Siddhi",      # 15
    "Vyatipata",   # 16 — inauspicious
    "Variyan",     # 17
    "Parigha",     # 18 — inauspicious
    "Shiva",       # 19
    "Siddha",      # 20
    "Sadhya",      # 21
    "Shubha",      # 22
    "Shukla",      # 23
    "Brahma",      # 24
    "Indra",       # 25
    "Vaidhriti",   # 26 — inauspicious
]

YOGA_SPAN_DEG: float = 360.0 / 27  # Same as Nakshatra span

BAD_YOGAS: FrozenSet[int] = frozenset({0, 5, 8, 9, 12, 14, 16, 18, 26})

# ---------------------------------------------------------------------------
# Karanas (60 half-tithis, but only 11 types cycle)
# First Karana of the cycle (index 0) starts at new moon
# ---------------------------------------------------------------------------
KARANA_NAMES: List[str] = [
    "Bava",      # 0
    "Balava",    # 1
    "Kaulava",   # 2
    "Taitila",   # 3
    "Garaja",    # 4
    "Vanija",    # 5
    "Vishti",    # 6  — Bhadra, inauspicious
    "Shakuni",   # 7  — fixed, always inauspicious for new starts
    "Chatushpada",# 8 — fixed
    "Naga",      # 9  — fixed
    "Kimstughna",# 10 — fixed (only at start of month)
]

BAD_KARANAS: FrozenSet[int] = frozenset({6, 7})  # Vishti (Bhadra) + Shakuni

# ---------------------------------------------------------------------------
# Tarabalam (9 Tara types, 1-indexed)
# ---------------------------------------------------------------------------
TARA_NAMES: Dict[int, str] = {
    1: "Janma",
    2: "Sampat",
    3: "Vipat",
    4: "Kshema",
    5: "Pratyak",
    6: "Sadhana",
    7: "Naidhana",
    8: "Mitra",
    9: "Parama Mitra",
}

# Taras that are inauspicious — REJECT any slot falling in these
BAD_TARAS: FrozenSet[int] = frozenset({1, 3, 5, 7})
# 1=Janma, 3=Vipat, 5=Pratyak, 7=Naidhana

# Taras considered auspicious (for activity mapping)
GOOD_TARAS: FrozenSet[int] = frozenset({2, 4, 6, 8, 9})

# ---------------------------------------------------------------------------
# Rahu Kalam / Yamaganda / Gulika Kalam
# Expressed as fractions of the daytime period (sunrise→sunset), per weekday
# Weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday (Python's datetime.weekday())
# ---------------------------------------------------------------------------

# Each tuple: (part_index, duration_parts)
# Day is divided into 8 equal parts. Each value is the 1-based part number.
RAHU_KALAM_PARTS: Dict[int, int] = {
    0: 2,  # Monday
    1: 7,  # Tuesday
    2: 5,  # Wednesday
    3: 6,  # Thursday
    4: 4,  # Friday
    5: 3,  # Saturday
    6: 8,  # Sunday
}

YAMAGANDA_PARTS: Dict[int, int] = {
    0: 5,  # Monday
    1: 4,  # Tuesday
    2: 3,  # Wednesday
    3: 2,  # Thursday
    4: 1,  # Friday
    5: 7,  # Saturday
    6: 6,  # Sunday
}

GULIKA_KALAM_PARTS: Dict[int, int] = {
    0: 6,  # Monday
    1: 5,  # Tuesday
    2: 4,  # Wednesday
    3: 3,  # Thursday
    4: 2,  # Friday
    5: 1,  # Saturday
    6: 7,  # Sunday
}

# Number of equal parts the day is divided into for Rahu/Yamaganda/Gulika
INAUSPICIOUS_PERIOD_PARTS: int = 8

# ---------------------------------------------------------------------------
# Activity tags per Tara type
# ---------------------------------------------------------------------------
TARA_ACTIVITY_MAP: Dict[int, List[str]] = {
    2: ["Business", "Finance", "Investments", "Agreements", "Purchases"],       # Sampat
    4: ["Health", "Travel", "Stability", "Property", "Long-term Plans"],        # Kshema
    6: ["Career", "Education", "Skills", "Daily Work", "Routine Tasks"],        # Sadhana
    8: ["Partnerships", "Networking", "Collaboration", "Interviews", "Social"], # Mitra
    9: ["Business", "Career", "Education", "Investments", "Property",           # Parama Mitra
        "Travel", "Surgery", "Housewarming", "New Ventures"],
}

# ---------------------------------------------------------------------------
# Slot configuration
# ---------------------------------------------------------------------------
SLOT_DURATION_MINUTES: int = 15  # Granularity of candidate time slots
