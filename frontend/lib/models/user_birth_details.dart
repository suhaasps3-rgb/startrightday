// lib/models/user_birth_details.dart
// Immutable value object for birth details entered by the user.

class UserBirthDetails {
  final String birthPlace;
  final DateTime birthDate;
  final String birthTime; // "HH:MM" 24-hour format
  final DateTime activityDate;

  const UserBirthDetails({
    required this.birthPlace,
    required this.birthDate,
    required this.birthTime,
    required this.activityDate,
  });

  /// Returns birthTime as a display string like "08:30 AM"
  String get birthTimeDisplay {
    final parts = birthTime.split(':');
    final hour = int.parse(parts[0]);
    final minute = parts[1];
    final period = hour >= 12 ? 'PM' : 'AM';
    final displayHour = hour % 12 == 0 ? 12 : hour % 12;
    return '$displayHour:$minute $period';
  }

  Map<String, dynamic> toJson() => {
        'birth_place': birthPlace,
        'birth_date': '${birthDate.year.toString().padLeft(4, '0')}-'
            '${birthDate.month.toString().padLeft(2, '0')}-'
            '${birthDate.day.toString().padLeft(2, '0')}',
        'birth_time': birthTime,
        'activity_date': '${activityDate.year.toString().padLeft(4, '0')}-'
            '${activityDate.month.toString().padLeft(2, '0')}-'
            '${activityDate.day.toString().padLeft(2, '0')}',
      };

  /// Serialized to SharedPreferences (without activity_date — that's per-query)
  Map<String, String> toStorageMap() => {
        'birth_place': birthPlace,
        'birth_date': birthDate.toIso8601String(),
        'birth_time': birthTime,
      };

  factory UserBirthDetails.fromStorageMap(
    Map<String, String> map,
    DateTime activityDate,
  ) {
    return UserBirthDetails(
      birthPlace: map['birth_place'] ?? '',
      birthDate: DateTime.parse(map['birth_date'] ?? DateTime.now().toIso8601String()),
      birthTime: map['birth_time'] ?? '06:00',
      activityDate: activityDate,
    );
  }

  UserBirthDetails copyWith({
    String? birthPlace,
    DateTime? birthDate,
    String? birthTime,
    DateTime? activityDate,
  }) {
    return UserBirthDetails(
      birthPlace: birthPlace ?? this.birthPlace,
      birthDate: birthDate ?? this.birthDate,
      birthTime: birthTime ?? this.birthTime,
      activityDate: activityDate ?? this.activityDate,
    );
  }
}
