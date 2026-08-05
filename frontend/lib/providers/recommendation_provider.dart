// lib/providers/recommendation_provider.dart
// AsyncNotifier that fetches recommendations from the API.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/recommendation_result.dart';
import '../models/user_birth_details.dart';
import '../services/api_service.dart';

final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

// ---------------------------------------------------------------------------
// Recommendation state
// ---------------------------------------------------------------------------
class RecommendationNotifier
    extends StateNotifier<AsyncValue<RecommendationResult?>> {
  final ApiService _api;

  RecommendationNotifier(this._api) : super(const AsyncValue.data(null));

  Future<void> fetch(UserBirthDetails details) async {
    state = const AsyncValue.loading();
    try {
      final result = await _api.recommend(details);
      state = AsyncValue.data(result);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  void reset() {
    state = const AsyncValue.data(null);
  }
}

final recommendationProvider = StateNotifierProvider<RecommendationNotifier,
    AsyncValue<RecommendationResult?>>((ref) {
  final api = ref.watch(apiServiceProvider);
  return RecommendationNotifier(api);
});
