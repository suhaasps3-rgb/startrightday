// lib/main.dart
// Application entry point.
// Initializes StorageService before runApp, then provides it via Riverpod override.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'providers/birth_details_provider.dart';
import 'services/storage_service.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Lock to portrait orientation for v1
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Set system UI overlay style (light status bar on dark splash, auto on rest)
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));

  // Initialize storage before runApp
  final storageService = await StorageService.create();

  runApp(
    ProviderScope(
      overrides: [
        // Inject the real StorageService instance
        storageServiceProvider.overrideWithValue(storageService),
      ],
      child: MaterialApp(
        title: 'StartRightDay',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: StartRightDayApp(storageService: storageService),
      ),
    ),
  );
}
