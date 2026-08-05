// lib/providers/birth_details_provider.dart
// Manages birth details state + persistence.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_birth_details.dart';
import '../services/storage_service.dart';

// ---------------------------------------------------------------------------
// StorageService provider — initialized in main.dart before runApp
// ---------------------------------------------------------------------------
final storageServiceProvider = Provider<StorageService>((ref) {
  throw UnimplementedError('StorageService must be overridden at app startup');
});

// ---------------------------------------------------------------------------
// Birth details notifier
// ---------------------------------------------------------------------------
class BirthDetailsNotifier extends StateNotifier<UserBirthDetails?> {
  final StorageService _storage;

  BirthDetailsNotifier(this._storage) : super(null) {
    _load();
  }

  void _load() {
    final saved = _storage.loadBirthDetails();
    if (saved != null) {
      state = saved;
    }
  }

  Future<void> update(UserBirthDetails details) async {
    state = details;
    await _storage.saveBirthDetails(details);
  }

  Future<void> updateActivityDate(DateTime date) async {
    if (state == null) return;
    final updated = state!.copyWith(activityDate: date);
    state = updated;
    // Activity date is not persisted — only birth details are
  }

  Future<void> clear() async {
    state = null;
    await _storage.clearBirthDetails();
  }
}

final birthDetailsProvider =
    StateNotifierProvider<BirthDetailsNotifier, UserBirthDetails?>((ref) {
  final storage = ref.watch(storageServiceProvider);
  return BirthDetailsNotifier(storage);
});
