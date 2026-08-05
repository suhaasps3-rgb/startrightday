// lib/models/recommendation_result.dart
// Dart model mirroring the FastAPI RecommendationResponse.
// All fields are nullable-safe with factory constructors.

class PanchangDetail {
  final String tara;
  final String tithi;
  final String yoga;
  final String karana;
  final String nakshatra;

  const PanchangDetail({
    required this.tara,
    required this.tithi,
    required this.yoga,
    required this.karana,
    required this.nakshatra,
  });

  factory PanchangDetail.fromJson(Map<String, dynamic> json) {
    return PanchangDetail(
      tara: json['tara'] as String,
      tithi: json['tithi'] as String,
      yoga: json['yoga'] as String,
      karana: json['karana'] as String,
      nakshatra: json['nakshatra'] as String,
    );
  }
}

class TimeInterval {
  final String startTime;
  final String endTime;
  final PanchangDetail panchang;
  final List<String> activities;

  const TimeInterval({
    required this.startTime,
    required this.endTime,
    required this.panchang,
    required this.activities,
  });

  factory TimeInterval.fromJson(Map<String, dynamic> json) {
    return TimeInterval(
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      panchang: PanchangDetail.fromJson(
        json['panchang'] as Map<String, dynamic>,
      ),
      activities: List<String>.from(json['activities'] as List),
    );
  }
}

enum RecommendationStatus { auspicious, avoid }

class RecommendationResult {
  final RecommendationStatus status;
  final List<TimeInterval> intervals;
  final String? message;
  final String? birthNakshatra;
  final String? activityDateDisplay;

  const RecommendationResult({
    required this.status,
    required this.intervals,
    this.message,
    this.birthNakshatra,
    this.activityDateDisplay,
  });

  bool get isAuspicious => status == RecommendationStatus.auspicious;

  factory RecommendationResult.fromJson(Map<String, dynamic> json) {
    final statusStr = json['status'] as String;
    final status = statusStr == 'auspicious'
        ? RecommendationStatus.auspicious
        : RecommendationStatus.avoid;

    final rawIntervals = json['intervals'] as List? ?? [];

    return RecommendationResult(
      status: status,
      intervals: rawIntervals
          .map((e) => TimeInterval.fromJson(e as Map<String, dynamic>))
          .toList(),
      message: json['message'] as String?,
      birthNakshatra: json['birth_nakshatra'] as String?,
      activityDateDisplay: json['activity_date_display'] as String?,
    );
  }
}
