# StartRightDay

> **Know the Best Time to Start.**

A production-quality mobile app that uses classical Vedic Panchang principles to determine auspicious time intervals for beginning important activities. Not an astrology app — a practical timing tool.

---

## Architecture

```
startrightday/
├── backend/          FastAPI + Swiss Ephemeris
└── frontend/         Flutter (Material 3)
```

---

## Backend Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API

```
POST http://localhost:8000/api/v1/recommend
Content-Type: application/json

{
  "birth_place": "Mumbai, India",
  "birth_date": "1990-06-15",
  "birth_time": "08:30",
  "activity_date": "2026-08-05"
}
```

**Response:**
```json
{
  "status": "auspicious",
  "intervals": [
    {
      "start_time": "7:15 AM",
      "end_time": "8:45 AM",
      "panchang": {
        "tara": "Sampat",
        "tithi": "Tritiya",
        "yoga": "Siddhi",
        "karana": "Bava",
        "nakshatra": "Rohini"
      },
      "activities": ["Business", "Finance", "Investments"]
    }
  ],
  "birth_nakshatra": "Punarvasu",
  "activity_date_display": "Wednesday, 5 August 2026"
}
```

Docs: `http://localhost:8000/docs`

---

## Frontend Setup

### Prerequisites
- Flutter 3.22+
- Dart 3.3+

### Installation

```bash
cd frontend
flutter pub get
```

### Configure API URL

Edit `lib/services/api_service.dart`:
```dart
static const String _baseUrl = 'http://10.0.2.2:8000'; // Android emulator
// static const String _baseUrl = 'http://localhost:8000'; // iOS simulator
```

### Run

```bash
flutter run
```

---

## Backend Module Map

| Module | Responsibility |
|--------|---------------|
| `constants.py` | All domain constants — zero logic |
| `models.py` | Pydantic request/response types |
| `location.py` | OSM geocoding + timezone resolution |
| `astronomy.py` | Swiss Ephemeris wrappers (Lahiri ayanamsa) |
| `panchang.py` | Nakshatra, Tithi, Yoga, Karana, Tara computation |
| `sunrise.py` | Sunrise/sunset, Rahu Kalam, Yamaganda, Gulika |
| `slot_engine.py` | 15-min candidate slot generator |
| `filters.py` | Rule-based rejection engine |
| `merger.py` | Contiguous slot merger |
| `timeline.py` | Activity recommendation mapper |
| `predictor.py` | Pipeline orchestrator (zero domain logic) |
| `main.py` | FastAPI entry, CORS, routes |

---

## Rules Implemented

| Rule | Status |
|------|--------|
| Tarabalam — reject Janma, Vipat, Pratyak, Naidhana | ✅ |
| Bad Tithis rejected | ✅ |
| Bad Yogas rejected | ✅ |
| Bad Karanas (Vishti/Bhadra, Shakuni) | ✅ |
| Rahu Kalam | ✅ |
| Yamaganda | ✅ |
| Gulika Kalam | ✅ |
| Durmuhurta | 🔜 |
| Varjyam | 🔜 |
| Abhijit Muhurta | 🔜 |
| Amrita Kalam | 🔜 |

---

## Frontend Screens

| Screen | Description |
|--------|-------------|
| Splash | Animated logo fade-in, navy background |
| Onboarding | 3 slides, productivity framing (no astrology) |
| Home | 4 input fields, "When should you begin?" |
| Loading | Rotating gradient arc + cycling Panchang messages |
| Result | Status banner, interval cards, activity chips |

---

## Design System

- **Palette**: Navy (`#0F172A`) + Indigo (`#6366F1`) + Clean white
- **Auspicious**: Emerald green (`#10B981`)
- **Avoid**: Amber (`#F59E0B`)
- **Typography**: Inter (Google Fonts)
- **Spacing**: 8-pt grid
- **No**: gold gradients, religious symbols, zodiac wheels, scores, percentages

---

## Engineering Standards

- All backend functions pure and typed
- No magic numbers — every constant named in `constants.py`
- Filters individually testable
- Riverpod state management — no setState in business logic
- Null-safe Flutter throughout
- Clean Architecture separation: UI ↔ Providers ↔ Services ↔ Models

---

## Planned Improvements (v2)

- [ ] Durmuhurta, Varjyam, Amrita Kalam filters
- [ ] Abhijit Muhurta detection
- [ ] Festival/eclipse exclusions
- [ ] Activity-specific date picker (select "Job Interview" → get best days this week)
- [ ] Push notification: "Today is auspicious for Business"
- [ ] Dark mode
- [ ] Widget (home screen reminder)
