// lib/app.dart
// Root app widget. Manages top-level navigation state without go_router
// for simplicity (5 screens, no deep linking needed at v1).

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'providers/birth_details_provider.dart';
import 'providers/recommendation_provider.dart';
import 'screens/home_screen.dart';
import 'screens/loading_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/result_screen.dart';
import 'screens/splash_screen.dart';
import 'services/storage_service.dart';
import 'theme/app_theme.dart';

enum _AppScreen { splash, onboarding, home, loading, result }

class StartRightDayApp extends ConsumerStatefulWidget {
  final StorageService storageService;

  const StartRightDayApp({super.key, required this.storageService});

  @override
  ConsumerState<StartRightDayApp> createState() => _StartRightDayAppState();
}

class _StartRightDayAppState extends ConsumerState<StartRightDayApp> {
  _AppScreen _screen = _AppScreen.splash;

  void _go(_AppScreen screen) => setState(() => _screen = screen);

  void _onSplashComplete() {
    final onboardingDone = widget.storageService.isOnboardingDone;
    _go(onboardingDone ? _AppScreen.home : _AppScreen.onboarding);
  }

  Future<void> _onOnboardingFinish() async {
    await widget.storageService.markOnboardingDone();
    _go(_AppScreen.home);
  }

  void _onCheckTime() => _go(_AppScreen.loading);

  void _onResult() => _go(_AppScreen.result);

  void _onError() => _go(_AppScreen.result); // Error displayed in result screen

  void _onBack() {
    ref.read(recommendationProvider.notifier).reset();
    _go(_AppScreen.home);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      switchInCurve: Curves.easeOut,
      switchOutCurve: Curves.easeIn,
      transitionBuilder: (child, animation) {
        return FadeTransition(opacity: animation, child: child);
      },
      child: _buildCurrentScreen(),
    );
  }

  Widget _buildCurrentScreen() {
    switch (_screen) {
      case _AppScreen.splash:
        return SplashScreen(key: const ValueKey('splash'), onComplete: _onSplashComplete);
      case _AppScreen.onboarding:
        return OnboardingScreen(key: const ValueKey('onboarding'), onFinish: _onOnboardingFinish);
      case _AppScreen.home:
        return HomeScreen(key: const ValueKey('home'), onCheckTime: _onCheckTime);
      case _AppScreen.loading:
        return LoadingScreen(
          key: const ValueKey('loading'),
          onResult: _onResult,
          onError: _onError,
        );
      case _AppScreen.result:
        return ResultScreen(key: const ValueKey('result'), onBack: _onBack);
    }
  }
}
