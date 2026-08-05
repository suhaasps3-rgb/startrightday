// lib/screens/home_screen.dart
// Main input screen — "When should you begin?"
// Four fields: Birth Place, Birth Date, Birth Time, Activity Date.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_birth_details.dart';
import '../providers/birth_details_provider.dart';
import '../providers/recommendation_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/common/primary_button.dart';
import '../widgets/input/date_field.dart';
import '../widgets/input/place_field.dart';
import '../widgets/input/time_field.dart';

class HomeScreen extends ConsumerStatefulWidget {
  final VoidCallback onCheckTime;

  const HomeScreen({super.key, required this.onCheckTime});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _placeController = TextEditingController();

  DateTime? _birthDate;
  TimeOfDay? _birthTime;
  DateTime? _activityDate;

  // Inline validation error messages
  String? _placeError;
  String? _birthDateError;
  String? _birthTimeError;
  String? _activityDateError;

  @override
  void initState() {
    super.initState();
    // Pre-populate from saved state
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final saved = ref.read(birthDetailsProvider);
      if (saved != null) {
        setState(() {
          _placeController.text = saved.birthPlace;
          _birthDate = saved.birthDate;
          final parts = saved.birthTime.split(':');
          _birthTime = TimeOfDay(
            hour: int.parse(parts[0]),
            minute: int.parse(parts[1]),
          );
          _activityDate = saved.activityDate;
        });
      } else {
        // Default activity date to today
        setState(() => _activityDate = DateTime.now());
      }
    });
  }

  @override
  void dispose() {
    _placeController.dispose();
    super.dispose();
  }

  bool _validate() {
    setState(() {
      _placeError =
          _placeController.text.trim().isEmpty ? 'Please enter a birth place' : null;
      _birthDateError = _birthDate == null ? 'Please select birth date' : null;
      _birthTimeError = _birthTime == null ? 'Please select birth time' : null;
      _activityDateError =
          _activityDate == null ? 'Please select activity date' : null;
    });
    return _placeError == null &&
        _birthDateError == null &&
        _birthTimeError == null &&
        _activityDateError == null;
  }

  Future<void> _submit() async {
    if (!_validate()) return;

    final details = UserBirthDetails(
      birthPlace: _placeController.text.trim(),
      birthDate: _birthDate!,
      birthTime:
          '${_birthTime!.hour.toString().padLeft(2, '0')}:${_birthTime!.minute.toString().padLeft(2, '0')}',
      activityDate: _activityDate!,
    );

    // Save birth details (not activity date)
    await ref.read(birthDetailsProvider.notifier).update(details);

    // Trigger recommendation fetch
    ref.read(recommendationProvider.notifier).fetch(details);

    widget.onCheckTime();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg,
            vertical: AppSpacing.xl,
          ),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                _buildHeader(),
                const SizedBox(height: AppSpacing.xxl),

                // Birth place
                PlaceField(
                  controller: _placeController,
                  errorText: _placeError,
                  onChanged: (_) => setState(() => _placeError = null),
                ),
                const SizedBox(height: AppSpacing.lg),

                // Birth date
                DateField(
                  label: 'Birth Date',
                  selectedDate: _birthDate,
                  firstDate: DateTime(1900),
                  lastDate: DateTime.now(),
                  hintText: 'Select your birth date',
                  errorText: _birthDateError,
                  onDateSelected: (d) => setState(() {
                    _birthDate = d;
                    _birthDateError = null;
                  }),
                ),
                const SizedBox(height: AppSpacing.lg),

                // Birth time
                TimeField(
                  label: 'Birth Time',
                  selectedTime: _birthTime,
                  errorText: _birthTimeError,
                  onTimeSelected: (t) => setState(() {
                    _birthTime = t;
                    _birthTimeError = null;
                  }),
                ),
                const SizedBox(height: AppSpacing.lg),

                // Activity date
                DateField(
                  label: 'Activity Date',
                  selectedDate: _activityDate,
                  firstDate: DateTime.now().subtract(const Duration(days: 1)),
                  lastDate: DateTime.now().add(const Duration(days: 365)),
                  hintText: 'When is your activity?',
                  errorText: _activityDateError,
                  onDateSelected: (d) => setState(() {
                    _activityDate = d;
                    _activityDateError = null;
                  }),
                ),
                const SizedBox(height: AppSpacing.xxl),

                // CTA
                PrimaryButton(
                  label: 'Check Best Time',
                  onPressed: _submit,
                  icon: Icons.arrow_forward_rounded,
                ),

                const SizedBox(height: AppSpacing.md),

                // Disclaimer
                Center(
                  child: Text(
                    'Based on classical Vedic Panchang principles',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: AppColors.textTertiary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Small label
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.accentSurface,
            borderRadius: BorderRadius.circular(AppRadius.full),
          ),
          child: Text(
            'PANCHANG TIMING',
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.accent,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.md),

        // Main heading
        Text(
          'When should\nyou begin?',
          style: AppTextStyles.displayLarge.copyWith(
            height: 1.15,
          ),
        ),
        const SizedBox(height: AppSpacing.sm),

        Text(
          'Enter your details to find the most aligned time for your activity.',
          style: AppTextStyles.bodyLarge.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}
