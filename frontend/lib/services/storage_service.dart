// lib/services/storage_service.dart
// Thin wrapper around SharedPreferences for persisting birth details.
// Activity date is NOT persisted — always defaults to today.

import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_birth_details.dart';

class StorageService {
  static const _keyBirthPlace = 'birth_place';
  static const _keyBirthDate = 'birth_date';
  static const _keyBirthTime = 'birth_time';
  static const _keyOnboardingDone = 'onboarding_done';

  final SharedPreferences _prefs;

  StorageService(this._prefs);

  static Future<StorageService> create() async {
    final prefs = await SharedPreferences.getInstance();
    return StorageService(prefs);
  }

  // ---------------------------------------------------------------------------
  // Birth details
  // ---------------------------------------------------------------------------

  Future<void> saveBirthDetails(UserBirthDetails details) async {
    await _prefs.setString(_keyBirthPlace, details.birthPlace);
    await _prefs.setString(_keyBirthDate, details.birthDate.toIso8601String());
    await _prefs.setString(_keyBirthTime, details.birthTime);
  }

  UserBirthDetails? loadBirthDetails() {
    final place = _prefs.getString(_keyBirthPlace);
    final dateStr = _prefs.getString(_keyBirthDate);
    final time = _prefs.getString(_keyBirthTime);

    if (place == null || dateStr == null || time == null) return null;
    if (place.isEmpty) return null;

    try {
      return UserBirthDetails(
        birthPlace: place,
        birthDate: DateTime.parse(dateStr),
        birthTime: time,
        activityDate: DateTime.now(),
      );
    } catch (_) {
      return null;
    }
  }

  Future<void> clearBirthDetails() async {
    await _prefs.remove(_keyBirthPlace);
    await _prefs.remove(_keyBirthDate);
    await _prefs.remove(_keyBirthTime);
  }

  // ---------------------------------------------------------------------------
  // Onboarding state
  // ---------------------------------------------------------------------------

  bool get isOnboardingDone => _prefs.getBool(_keyOnboardingDone) ?? false;

  Future<void> markOnboardingDone() async {
    await _prefs.setBool(_keyOnboardingDone, true);
  }
}
